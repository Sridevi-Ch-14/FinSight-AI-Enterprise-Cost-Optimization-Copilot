"""
text_to_sql.py  –  Production-grade hybrid Text-to-SQL for FinSight AI
=======================================================================

Pipeline per request
--------------------
1. Rule engine  (regex, zero latency, zero cost)
        ↓ miss
2. LLM SQL generation  (schema-grounded prompt + few-shot + conversation history)
        ↓
3. Schema validator  (whitelist check – blocks hallucinated tables/columns)
        ↓
4. Safety validator  (blocks DROP / DELETE / ALTER etc.)
        ↓
5. Execute on MySQL
        ↓
6. Explanation generator  (second LLM call, 1-sentence plain-English summary)
"""

import re
import os
import json
import logging
from collections import defaultdict, deque
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1.  SCHEMA GROUND-TRUTH  (single source of truth – mirrors models.py exactly)
# ─────────────────────────────────────────────────────────────────────────────

# Used for: prompt injection AND column/table whitelist validation
SCHEMA: dict[str, list[str]] = {
    "departments":        ["id", "name"],
    "vendors":            ["id", "vendor_name", "normalized_name", "category",
                           "benchmark_cost", "risk_score"],
    "spend_transactions": ["id", "department_id", "vendor_id", "date",
                           "amount", "spend_type", "payment_type"],
    "subscriptions":      ["id", "vendor_id", "department_id", "plan_tier",
                           "seat_count", "monthly_cost"],
    "contracts":          ["id", "vendor_id", "contract_name", "renewal_date",
                           "annual_value", "auto_renew", "department_owner"],
    "recommendations":    ["id", "vendor_id", "recommendation_type",
                           "projected_savings", "rationale", "risk_level",
                           "alternative_vendor", "feature_parity"],
    "chat_queries":       ["id", "question", "generated_sql", "result",
                           "session_id", "explanation", "created_at"],
}

# Flat sets for O(1) lookup
_ALL_TABLES  = set(SCHEMA.keys())
_ALL_COLUMNS = {col for cols in SCHEMA.values() for col in cols}

# Human-readable schema block injected into every LLM prompt
_SCHEMA_BLOCK = "\n".join(
    f"  {tbl}({', '.join(cols)})"
    for tbl, cols in SCHEMA.items()
)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  PRODUCTION PROMPT TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a MySQL query generator for FinSight AI, an enterprise spend-intelligence platform.

━━━ DATABASE SCHEMA (MySQL 8.0) ━━━
{schema}

━━━ STRICT RULES ━━━
1. Output ONLY a single SQL SELECT statement — no explanation, no markdown, no comments.
2. Use ONLY the tables and columns listed in the schema above. Never invent columns.
3. Always qualify column names with table alias (e.g. v.vendor_name, not just vendor_name).
4. Use MySQL syntax: CURDATE(), DATE_ADD(), INTERVAL, YEAR(), MONTH().
5. Never use: DROP, DELETE, TRUNCATE, ALTER, CREATE, INSERT, UPDATE, GRANT, REVOKE.
6. For monetary amounts always SUM(st.amount) — never AVG unless explicitly asked.
7. Always add ORDER BY for ranked/top queries. Always add LIMIT when user says "top N".
8. For date ranges use: WHERE st.date BETWEEN '...' AND '...' or YEAR(st.date) = YEAR(CURDATE()).
9. When joining vendors↔spend_transactions use: JOIN spend_transactions st ON v.id = st.vendor_id
10. End the query with a semicolon.

━━━ FEW-SHOT EXAMPLES ━━━
Q: Top 5 vendors by spend
SQL: SELECT v.vendor_name, SUM(st.amount) AS total_spend FROM vendors v JOIN spend_transactions st ON v.id = st.vendor_id GROUP BY v.id, v.vendor_name ORDER BY total_spend DESC LIMIT 5;

Q: Which categories have redundancy?
SQL: SELECT v.category, COUNT(DISTINCT v.id) AS vendor_count, SUM(st.amount) AS total_spend FROM vendors v JOIN spend_transactions st ON v.id = st.vendor_id WHERE v.category IS NOT NULL GROUP BY v.category HAVING vendor_count > 1 ORDER BY vendor_count DESC;

Q: Renewals in next 90 days
SQL: SELECT v.vendor_name, c.renewal_date, c.annual_value, c.auto_renew FROM contracts c JOIN vendors v ON c.vendor_id = v.id WHERE c.renewal_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 90 DAY) ORDER BY c.renewal_date;

Q: Spend by department
SQL: SELECT d.name AS department, SUM(st.amount) AS total_spend FROM departments d JOIN spend_transactions st ON d.id = st.department_id GROUP BY d.id, d.name ORDER BY total_spend DESC;

Q: Total spend this year
SQL: SELECT SUM(st.amount) AS total_spend FROM spend_transactions st WHERE YEAR(st.date) = YEAR(CURDATE());

Q: Total spend last year
SQL: SELECT SUM(st.amount) AS total_spend FROM spend_transactions st WHERE YEAR(st.date) = YEAR(CURDATE()) - 1;

Q: Vendors with high risk score
SQL: SELECT v.vendor_name, v.category, v.risk_score FROM vendors v WHERE v.risk_score > 0.7 ORDER BY v.risk_score DESC;

Q: Monthly subscription cost by department
SQL: SELECT d.name AS department, SUM(s.monthly_cost) AS total_monthly FROM subscriptions s JOIN departments d ON s.department_id = d.id GROUP BY d.id, d.name ORDER BY total_monthly DESC;

Q: Contracts with auto-renew enabled above 1 million
SQL: SELECT v.vendor_name, c.contract_name, c.annual_value, c.renewal_date FROM contracts c JOIN vendors v ON c.vendor_id = v.id WHERE c.auto_renew = TRUE AND c.annual_value > 1000000 ORDER BY c.annual_value DESC;

Q: Top savings recommendations
SQL: SELECT v.vendor_name, r.recommendation_type, r.projected_savings, r.risk_level, r.alternative_vendor FROM recommendations r JOIN vendors v ON r.vendor_id = v.id ORDER BY r.projected_savings DESC LIMIT 10;
""".strip()

_EXPLANATION_PROMPT = """\
You are a finance analyst assistant. Given a SQL query and its results, write ONE concise sentence \
(max 25 words) explaining what the data shows. Be specific — mention numbers if available. \
Do not say "the query" or "the SQL". Start directly with the insight.

SQL: {sql}
Results (first 3 rows): {sample}
Explanation:""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# 3.  CONVERSATIONAL MEMORY  (in-process, session-scoped, last 3 turns)
# ─────────────────────────────────────────────────────────────────────────────

# { session_id: deque([{"question": ..., "sql": ...}, ...], maxlen=3) }
_SESSION_MEMORY: dict[str, deque] = defaultdict(lambda: deque(maxlen=3))


def _get_history_block(session_id: Optional[str]) -> str:
    """Return a formatted conversation history block for the prompt, or empty string."""
    if not session_id:
        return ""
    history = _SESSION_MEMORY.get(session_id)
    if not history:
        return ""
    lines = ["━━━ CONVERSATION HISTORY (use for follow-up context) ━━━"]
    for i, turn in enumerate(history, 1):
        lines.append(f"Turn {i} — Q: {turn['question']}")
        lines.append(f"         SQL: {turn['sql']}")
    return "\n".join(lines)


def _save_to_memory(session_id: Optional[str], question: str, sql: str) -> None:
    if session_id:
        _SESSION_MEMORY[session_id].append({"question": question, "sql": sql})


# ─────────────────────────────────────────────────────────────────────────────
# 4.  SCHEMA VALIDATOR  (whitelist — catches hallucinated tables/columns)
# ─────────────────────────────────────────────────────────────────────────────

# Matches bare identifiers that are NOT inside quotes or functions
_IDENTIFIER_RE = re.compile(r'\b([a-z_][a-z0-9_]*)\b', re.IGNORECASE)

# SQL keywords to skip during identifier scanning
_SQL_KEYWORDS = {
    "select", "from", "where", "join", "on", "group", "by", "order", "having",
    "limit", "offset", "as", "and", "or", "not", "in", "is", "null", "true",
    "false", "between", "like", "case", "when", "then", "else", "end", "inner",
    "left", "right", "outer", "cross", "distinct", "count", "sum", "avg", "min",
    "max", "coalesce", "ifnull", "year", "month", "day", "curdate", "date_add",
    "date_sub", "interval", "asc", "desc", "int", "varchar", "float", "date",
    "datetime", "boolean", "text", "char", "union", "all", "exists", "with",
}


def _validate_schema(sql: str) -> None:
    """
    Scan every identifier in the SQL.
    Raise ValueError if a word looks like a table or column name that isn't in SCHEMA.
    Strategy: flag identifiers that are NOT keywords AND NOT in our whitelist
    AND appear to be used as table/column references (preceded by FROM/JOIN/. or followed by .).
    """
    sql_lower = sql.lower()

    # Check table names explicitly (words after FROM / JOIN)
    table_refs = re.findall(
        r'\b(?:from|join)\s+([a-z_][a-z0-9_]*)', sql_lower
    )
    for tbl in table_refs:
        if tbl not in _ALL_TABLES and tbl not in _SQL_KEYWORDS:
            raise ValueError(
                f"Hallucination detected: table '{tbl}' does not exist in the schema. "
                f"Valid tables: {sorted(_ALL_TABLES)}"
            )

    # Check column names (words after a dot: alias.column_name)
    col_refs = re.findall(r'[a-z_][a-z0-9_]*\.([a-z_][a-z0-9_]*)', sql_lower)
    for col in col_refs:
        if col not in _ALL_COLUMNS and col not in _SQL_KEYWORDS:
            raise ValueError(
                f"Hallucination detected: column '{col}' does not exist in any table. "
                f"Check the schema for valid column names."
            )


# ─────────────────────────────────────────────────────────────────────────────
# 5.  SAFETY VALIDATOR  (blocks destructive SQL)
# ─────────────────────────────────────────────────────────────────────────────

_BLOCKED_KEYWORDS = re.compile(
    r'\b(DROP|DELETE|TRUNCATE|ALTER|CREATE|INSERT|UPDATE|GRANT|REVOKE|EXEC|EXECUTE|LOAD|OUTFILE)\b',
    re.IGNORECASE,
)


def _validate_safety(sql: str) -> str:
    """Strip trailing semicolon, assert SELECT-only, assert no destructive keywords."""
    clean = sql.strip().rstrip(';').strip()
    if not clean.upper().lstrip().startswith('SELECT'):
        raise ValueError(f"Only SELECT statements are permitted. Received: {clean[:80]}")
    if _BLOCKED_KEYWORDS.search(clean):
        raise ValueError("Query contains a blocked keyword (DROP/DELETE/ALTER/INSERT etc.)")
    return clean


def _extract_sql(raw: str) -> str:
    """Extract the first SQL SELECT from an LLM response (handles fenced and plain)."""
    # ```sql ... ``` or ``` ... ```
    fenced = re.search(r'```(?:sql)?\s*(SELECT[\s\S]+?)```', raw, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()
    # Bare SELECT ... ; on one or multiple lines
    bare = re.search(r'(SELECT[\s\S]+?;)', raw, re.IGNORECASE)
    if bare:
        return bare.group(1).strip()
    # Last resort: everything from SELECT to end
    last = re.search(r'(SELECT[\s\S]+)', raw, re.IGNORECASE)
    if last:
        return last.group(1).strip()
    raise ValueError("LLM response contained no recognisable SELECT statement.")


# ─────────────────────────────────────────────────────────────────────────────
# 6.  LLM CLIENT  (lazy, supports OpenAI + Ollama via same interface)
# ─────────────────────────────────────────────────────────────────────────────

def _get_client():
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("Run: pip install groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("Set GROQ_API_KEY in .env")

    return Groq(api_key=api_key)


def _chat(messages: list[dict], max_tokens: int = 512) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama3-8b-8192"),
        messages=messages,
        temperature=0,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content.strip()


# ─────────────────────────────────────────────────────────────────────────────
# 7.  LLM SQL GENERATION  (with retry — each attempt re-validates)
# ─────────────────────────────────────────────────────────────────────────────

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6),
    retry=retry_if_exception_type(ValueError),
    reraise=True,
)
def _llm_generate_sql(question: str, session_id: Optional[str]) -> str:
    history_block = _get_history_block(session_id)

    user_content = (
        f"{history_block}\n\n" if history_block else ""
    ) + f"Question: {question}\nSQL:"

    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT.format(schema=_SCHEMA_BLOCK)},
        {"role": "user",   "content": user_content},
    ]

    raw = _chat(messages)
    sql = _extract_sql(raw)
    sql = _validate_safety(sql)   # raises ValueError → triggers retry
    _validate_schema(sql)         # raises ValueError → triggers retry
    return sql


# ─────────────────────────────────────────────────────────────────────────────
# 8.  EXPLANATION GENERATOR  (single cheap LLM call after execution)
# ─────────────────────────────────────────────────────────────────────────────

def _generate_explanation(sql: str, data: list[dict]) -> str:
    """Generate a 1-sentence plain-English explanation of the query results."""
    if not data:
        return "No data was found matching your query."

    llm_enabled = bool(os.getenv("GROQ_API_KEY"))
    if not llm_enabled:
        # Rule-based fallback explanation
        row_count = len(data)
        cols = list(data[0].keys()) if data else []
        return f"Query returned {row_count} row(s) with columns: {', '.join(cols)}."

    try:
        sample = json.dumps(data[:3], default=str)
        prompt = _EXPLANATION_PROMPT.format(sql=sql, sample=sample)
        explanation = _chat(
            [{"role": "user", "content": prompt}],
            max_tokens=80,
        )
        # Strip any accidental "Explanation:" prefix the model echoes back
        return re.sub(r'^explanation:\s*', '', explanation, flags=re.IGNORECASE).strip()
    except Exception as exc:
        logger.warning("Explanation generation failed: %s", exc)
        return f"Query returned {len(data)} row(s)."


# ─────────────────────────────────────────────────────────────────────────────
# 9.  RULE ENGINE  (fast path — zero latency, zero cost)
# ─────────────────────────────────────────────────────────────────────────────

_RULE_PATTERNS = [
    {
        "pattern": r"top\s+(\d+)\s+vendors?\s+by\s+(?:annual\s+)?spend",
        "sql": (
            "SELECT v.vendor_name, SUM(st.amount) AS total_spend "
            "FROM vendors v JOIN spend_transactions st ON v.id = st.vendor_id "
            "GROUP BY v.id, v.vendor_name ORDER BY total_spend DESC LIMIT {0}"
        ),
        "groups": [1],
    },
    {
        "pattern": r"which\s+categories?\s+have\s+redundancy",
        "sql": (
            "SELECT v.category, COUNT(DISTINCT v.id) AS vendor_count, "
            "SUM(st.amount) AS total_spend "
            "FROM vendors v JOIN spend_transactions st ON v.id = st.vendor_id "
            "WHERE v.category IS NOT NULL GROUP BY v.category "
            "HAVING vendor_count > 1 ORDER BY vendor_count DESC"
        ),
        "groups": [],
    },
    {
        "pattern": r"how\s+much\s+can\s+we\s+save\s+by\s+consolidation",
        "sql": (
            "SELECT SUM(r.projected_savings) AS total_savings "
            "FROM recommendations r WHERE r.recommendation_type = 'consolidation'"
        ),
        "groups": [],
    },
    {
        "pattern": r"(?:list\s+)?renewals?\s+in\s+(?:the\s+)?next\s+(\d+)\s+days",
        "sql": (
            "SELECT v.vendor_name, c.renewal_date, c.annual_value, c.auto_renew "
            "FROM contracts c JOIN vendors v ON c.vendor_id = v.id "
            "WHERE c.renewal_date BETWEEN CURDATE() "
            "AND DATE_ADD(CURDATE(), INTERVAL {0} DAY) ORDER BY c.renewal_date"
        ),
        "groups": [1],
    },
    {
        "pattern": r"total\s+(?:annual\s+)?spend\s+(?:this|current)\s+year",
        "sql": (
            "SELECT SUM(st.amount) AS total_spend FROM spend_transactions st "
            "WHERE YEAR(st.date) = YEAR(CURDATE())"
        ),
        "groups": [],
    },
    {
        "pattern": r"total\s+(?:annual\s+)?spend\s+last\s+year",
        "sql": (
            "SELECT SUM(st.amount) AS total_spend FROM spend_transactions st "
            "WHERE YEAR(st.date) = YEAR(CURDATE()) - 1"
        ),
        "groups": [],
    },
    {
        "pattern": r"total\s+(?:annual\s+)?spend",
        "sql": "SELECT SUM(st.amount) AS total_spend FROM spend_transactions st",
        "groups": [],
    },
    {
        "pattern": r"spend\s+by\s+department",
        "sql": (
            "SELECT d.name AS department, SUM(st.amount) AS total_spend "
            "FROM departments d JOIN spend_transactions st ON d.id = st.department_id "
            "GROUP BY d.id, d.name ORDER BY total_spend DESC"
        ),
        "groups": [],
    },
    {
        "pattern": r"spend\s+by\s+category",
        "sql": (
            "SELECT v.category, SUM(st.amount) AS total_spend "
            "FROM vendors v JOIN spend_transactions st ON v.id = st.vendor_id "
            "WHERE v.category IS NOT NULL GROUP BY v.category ORDER BY total_spend DESC"
        ),
        "groups": [],
    },
    {
        "pattern": r"shadow\s+it",
        "sql": (
            "SELECT v.vendor_name, d.name AS department, SUM(st.amount) AS spend "
            "FROM vendors v "
            "JOIN spend_transactions st ON v.id = st.vendor_id "
            "JOIN departments d ON st.department_id = d.id "
            "GROUP BY v.id, v.vendor_name, d.id, d.name "
            "HAVING COUNT(DISTINCT st.department_id) = 1 ORDER BY spend DESC"
        ),
        "groups": [],
    },
    {
        "pattern": r"top\s+(\d+)\s+(?:cost\s+)?(?:saving|savings?|recommendation)",
        "sql": (
            "SELECT v.vendor_name, r.recommendation_type, r.projected_savings, "
            "r.risk_level, r.alternative_vendor "
            "FROM recommendations r JOIN vendors v ON r.vendor_id = v.id "
            "ORDER BY r.projected_savings DESC LIMIT {0}"
        ),
        "groups": [1],
    },
]


def _try_rule_engine(question: str) -> Optional[str]:
    q = question.lower().strip()
    for rule in _RULE_PATTERNS:
        m = re.search(rule["pattern"], q)
        if m:
            sql = rule["sql"]
            for idx in rule["groups"]:
                sql = sql.replace(f"{{{idx-1}}}", m.group(idx), 1) if idx > 0 else sql
            # Simple positional replacement for {0}
            if "{0}" in sql and m.lastindex and m.lastindex >= 1:
                sql = sql.replace("{0}", m.group(1))
            return sql
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 10.  PUBLIC SERVICE
# ─────────────────────────────────────────────────────────────────────────────

class TextToSQLService:
    """
    Hybrid Text-to-SQL service.

    generate_sql(question, session_id) → dict
    execute_query(db, sql_result)      → dict  (includes explanation)
    """

    def generate_sql(self, question: str, session_id: Optional[str] = None) -> dict:
        """
        Returns:
            {
                "sql":        str | None,
                "source":     "rule" | "llm" | "error",
                "session_id": str | None,
                "error":      str | None,
            }
        """
        # ── Fast path: rule engine ──
        sql = _try_rule_engine(question)
        if sql:
            logger.info("[rule] matched: %.80s", question)
            _save_to_memory(session_id, question, sql)
            return {"sql": sql, "source": "rule", "session_id": session_id, "error": None}

        # ── LLM path ──
        llm_enabled = bool(os.getenv("GROQ_API_KEY"))
        if not llm_enabled:
            return {
                "sql": None, "source": "error", "session_id": session_id,
                "error": "Query not matched by rule engine and LLM is not configured. "
                         "Set OPENAI_API_KEY in .env to enable AI queries.",
            }

        try:
            sql = _llm_generate_sql(question, session_id)
            logger.info("[llm] generated SQL for: %.80s", question)
            _save_to_memory(session_id, question, sql)
            return {"sql": sql, "source": "llm", "session_id": session_id, "error": None}
        except ValueError as ve:
            # Schema/safety validation failed after all retries
            logger.warning("[llm] validation failed: %s", ve)
            return {"sql": None, "source": "error", "session_id": session_id, "error": str(ve)}
        except Exception as exc:
            logger.error("[llm] failed after retries: %s", exc)
            return {"sql": None, "source": "error", "session_id": session_id, "error": str(exc)}

    def execute_query(self, db: Session, sql_result: dict) -> dict:
        """
        Executes the SQL from generate_sql() output.

        Returns:
            {
                "success":     bool,
                "data":        list[dict],
                "columns":     list[str],
                "source":      str,
                "explanation": str,
                "error":       str | None,
            }
        """
        _empty = {"success": False, "data": [], "columns": [],
                  "source": "error", "explanation": "", "error": None}

        if sql_result.get("source") == "error" or not sql_result.get("sql"):
            return {**_empty, "error": sql_result.get("error", "No SQL generated")}

        sql = sql_result["sql"]

        # Final safety + schema gate before touching the DB
        try:
            sql = _validate_safety(sql)
            _validate_schema(sql)
        except ValueError as ve:
            return {**_empty, "error": str(ve)}

        try:
            res     = db.execute(text(sql))
            rows    = res.fetchall()
            columns = list(res.keys())
            data    = [dict(zip(columns, row)) for row in rows]

            explanation = _generate_explanation(sql, data)

            return {
                "success":     True,
                "data":        data,
                "columns":     columns,
                "source":      sql_result["source"],
                "explanation": explanation,
                "error":       None,
            }
        except Exception as exc:
            logger.error("[exec] SQL error: %s | sql: %s", exc, sql)
            return {**_empty, "error": str(exc)}
