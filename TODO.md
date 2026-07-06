# TODO - Push necessary files to target GitHub repo

## Plan Summary (approved)
- Create a minimal archive containing core project files.
- Exclude typical local artifacts (e.g., .venv).
- Upload/push to the target repo using a temporary Git repo (since current folder is not a git repo).

## Steps
1. Verify whether current directory is a git repo; if not, create a new temp git repo.
2. Create an archive (or staging) of required files only:
   - README.md + other root .md files (per user: “only push README.md in .md files”)
   - docker-compose.yml
   - backend/
   - frontend/
   - database/
   - .gitignore (if present)
   - exclude .venv/
3. Initialize git in this folder (or staging folder) and commit.
4. Add remote to `https://github.com/Sridevi-Ch-14/FinSight-AI-Enterprise-Cost-Optimization-Copilot.git`.
5. Create/force-push to default branch (or confirm branch behavior).
6. Verify remote contains only the intended files.

