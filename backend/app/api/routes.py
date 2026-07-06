from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config.database import get_db
from app.models.models import Vendor, SpendTransaction, Subscription, Contract, Recommendation, Department, ChatQuery
from app.services.upload_service import DataUploadService
from app.services.recommendation_engine import RecommendationEngine
from app.services.text_to_sql import TextToSQLService
from app.services.shadow_it_detector import ShadowITDetector
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()

# Upload endpoints
@router.post("/upload/spend")
async def upload_spend(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload vendor spend CSV"""
    content = await file.read()
    service = DataUploadService(db)
    result = service.process_spend_csv(content)
    
    if result['success']:
        # Generate recommendations after upload
        engine = RecommendationEngine(db)
        engine.generate_all_recommendations()
    
    return result

@router.post("/upload/subscriptions")
async def upload_subscriptions(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload SaaS subscription CSV"""
    content = await file.read()
    service = DataUploadService(db)
    result = service.process_subscription_csv(content)
    
    if result['success']:
        engine = RecommendationEngine(db)
        engine.generate_all_recommendations()
    
    return result

@router.post("/upload/contracts")
async def upload_contracts(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload contract renewal CSV"""
    content = await file.read()
    service = DataUploadService(db)
    result = service.process_contract_csv(content)
    
    if result['success']:
        engine = RecommendationEngine(db)
        engine.generate_all_recommendations()
    
    return result

# Dashboard endpoints
@router.get("/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get dashboard summary statistics"""
    total_spend = db.query(func.sum(SpendTransaction.amount)).scalar() or 0
    
    # Only show savings if spend data exists
    if total_spend > 0:
        total_savings = db.query(func.sum(Recommendation.projected_savings)).scalar() or 0
    else:
        total_savings = 0
    
    redundant_vendors = db.query(func.count(func.distinct(Recommendation.vendor_id))).filter(
        Recommendation.recommendation_type == 'consolidation'
    ).scalar() or 0
    
    upcoming_renewals = db.query(func.count(Contract.id)).filter(
        Contract.renewal_date <= datetime.now().date() + timedelta(days=90),
        Contract.renewal_date >= datetime.now().date()
    ).scalar() or 0
    
    # Spend by vendor (top 10)
    spend_by_vendor = db.query(
        Vendor.vendor_name,
        func.sum(SpendTransaction.amount).label('total')
    ).join(SpendTransaction).group_by(
        Vendor.id, Vendor.vendor_name
    ).order_by(func.sum(SpendTransaction.amount).desc()).limit(10).all()
    
    # Spend by department
    spend_by_dept = db.query(
        Department.name,
        func.sum(SpendTransaction.amount).label('total')
    ).join(SpendTransaction).group_by(
        Department.id, Department.name
    ).order_by(func.sum(SpendTransaction.amount).desc()).all()
    
    # Spend by category
    spend_by_category = db.query(
        Vendor.category,
        func.sum(SpendTransaction.amount).label('total')
    ).join(SpendTransaction).filter(
        Vendor.category.isnot(None)
    ).group_by(Vendor.category).order_by(
        func.sum(SpendTransaction.amount).desc()
    ).all()
    
    return {
        "summary": {
            "total_annual_spend": total_spend,
            "identified_savings": total_savings,
            "redundant_vendors": redundant_vendors,
            "upcoming_renewals": upcoming_renewals
        },
        "spend_by_vendor": [{"name": v, "value": float(t)} for v, t in spend_by_vendor],
        "spend_by_department": [{"name": d, "value": float(t)} for d, t in spend_by_dept],
        "spend_by_category": [{"name": c, "value": float(t)} for c, t in spend_by_category]
    }

# Vendor redundancy
@router.get("/vendors/redundancy")
def get_vendor_redundancy(db: Session = Depends(get_db)):
    """Get vendor redundancy analysis with correct counts"""
    redundancy = db.query(
        Vendor.category,
        func.count(func.distinct(Vendor.id)).label('vendor_count'),
        func.count(SpendTransaction.id).label('transaction_count'),
        func.sum(SpendTransaction.amount).label('total_spend')
    ).join(SpendTransaction).filter(
        Vendor.category.isnot(None)
    ).group_by(Vendor.category).having(
        func.count(func.distinct(Vendor.id)) > 1
    ).order_by(func.count(func.distinct(Vendor.id)).desc()).all()
    
    result = []
    for category, vendor_count, transaction_count, spend in redundancy:
        vendors = db.query(Vendor.vendor_name).join(SpendTransaction).filter(
            Vendor.category == category
        ).distinct().all()
        
        result.append({
            "category": category,
            "vendor_count": vendor_count,
            "transaction_count": transaction_count,
            "total_spend": float(spend),
            "vendors": [v[0] for v in vendors]
        })
    
    return result

# Recommendations
@router.get("/recommendations/top")
def get_top_recommendations(db: Session = Depends(get_db)):
    """Get top cost optimization recommendations"""
    recommendations = db.query(Recommendation).join(Vendor).order_by(
        Recommendation.projected_savings.desc()
    ).limit(20).all()
    
    result = []
    for rec in recommendations:
        vendor = db.query(Vendor).filter(Vendor.id == rec.vendor_id).first()
        result.append({
            "id": rec.id,
            "vendor": vendor.vendor_name,
            "type": rec.recommendation_type,
            "savings": float(rec.projected_savings),
            "rationale": rec.rationale,
            "risk_level": rec.risk_level,
            "alternative": rec.alternative_vendor,
            "feature_parity": rec.feature_parity
        })
    
    return result

# Contract renewals
@router.get("/contracts/upcoming-renewals")
def get_upcoming_renewals(db: Session = Depends(get_db)):
    """Get upcoming contract renewals with risk scoring"""
    upcoming = datetime.now().date() + timedelta(days=90)
    contracts = db.query(Contract).join(Vendor).filter(
        Contract.renewal_date <= upcoming,
        Contract.renewal_date >= datetime.now().date()
    ).order_by(Contract.renewal_date).all()
    
    result = []
    for contract in contracts:
        vendor = db.query(Vendor).filter(Vendor.id == contract.vendor_id).first()
        days_until = (contract.renewal_date - datetime.now().date()).days
        
        # Risk scoring
        risk_level = 'Low'
        if contract.auto_renew and contract.annual_value > 5000000 and days_until <= 60:
            risk_level = 'High'
        elif days_until <= 90:
            risk_level = 'Medium'
        
        result.append({
            "vendor": vendor.vendor_name,
            "contract_name": contract.contract_name or vendor.vendor_name,
            "renewal_date": contract.renewal_date.isoformat(),
            "annual_value": float(contract.annual_value),
            "auto_renew": contract.auto_renew,
            "department_owner": contract.department_owner,
            "days_until": days_until,
            "risk_level": risk_level
        })
    
    return result

@router.get("/shadow-it/detect")
def detect_shadow_it(db: Session = Depends(get_db)):
    """Detect shadow IT spend"""
    detector = ShadowITDetector(db)
    return detector.detect_shadow_it()

# Finance Copilot
class CopilotQuery(BaseModel):
    question: str
    session_id: str | None = None   # pass same ID across turns for follow-up context

@router.post("/copilot/query")
def copilot_query(query: CopilotQuery, db: Session = Depends(get_db)):
    """Process natural language query via hybrid rule+LLM engine with memory"""
    service = TextToSQLService()
    sql_result = service.generate_sql(query.question, session_id=query.session_id)
    result     = service.execute_query(db, sql_result)

    chat_query = ChatQuery(
        question      = query.question,
        generated_sql = sql_result.get("sql") or "",
        result        = str(result.get("data", [])),
        session_id    = query.session_id,
        explanation   = result.get("explanation", ""),
    )
    db.add(chat_query)
    db.commit()

    return {
        "question":    query.question,
        "sql":         sql_result.get("sql"),
        "source":      sql_result.get("source"),      # "rule" | "llm" | "error"
        "session_id":  query.session_id,
        "explanation": result.get("explanation"),     # plain-English summary
        "result":      result,
    }

@router.get("/copilot/history")
def get_copilot_history(db: Session = Depends(get_db)):
    """Get query history"""
    queries = db.query(ChatQuery).order_by(
        ChatQuery.created_at.desc()
    ).limit(20).all()

    return [{
        "id":          q.id,
        "question":    q.question,
        "sql":         q.generated_sql,
        "explanation": q.explanation,
        "session_id":  q.session_id,
        "created_at":  q.created_at.isoformat()
    } for q in queries]

# Reports
@router.get("/reports/export")
def export_report(db: Session = Depends(get_db)):
    """Export executive report data"""
    summary = get_dashboard_summary(db)
    recommendations = get_top_recommendations(db)
    renewals = get_upcoming_renewals(db)
    
    return {
        "summary": summary,
        "recommendations": recommendations,
        "renewals": renewals,
        "generated_at": datetime.now().isoformat()
    }

# Data Management
@router.get("/data/stats")
def get_data_stats(db: Session = Depends(get_db)):
    """Get uploaded data statistics"""
    spend_count = db.query(func.count(SpendTransaction.id)).scalar() or 0
    subscription_count = db.query(func.count(Subscription.id)).scalar() or 0
    contract_count = db.query(func.count(Contract.id)).scalar() or 0
    
    return {
        "spend_transactions": spend_count,
        "subscriptions": subscription_count,
        "contracts": contract_count
    }

@router.delete("/data/clear/{data_type}")
def clear_data(data_type: str, db: Session = Depends(get_db)):
    """Clear specific data type from database"""
    try:
        if data_type == "spend":
            db.query(SpendTransaction).delete()
        elif data_type == "subscriptions":
            db.query(Subscription).delete()
        elif data_type == "contracts":
            db.query(Contract).delete()
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        # Clear recommendations when data is deleted
        db.query(Recommendation).delete()
        db.commit()
        
        return {"success": True, "message": f"{data_type} data cleared successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
