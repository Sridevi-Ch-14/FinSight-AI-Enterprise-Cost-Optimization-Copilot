from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Vendor, SpendTransaction, Department

class ShadowITDetector:
    """Detect shadow IT spend - vendors purchased by single departments"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_shadow_it(self, min_spend_threshold=500000):
        """
        Detect vendors purchased by only one department
        Returns list of potential shadow IT vendors
        """
        results = []
        
        vendors = self.db.query(Vendor).all()
        
        for vendor in vendors:
            # Count distinct departments purchasing this vendor
            dept_count = self.db.query(
                func.count(func.distinct(SpendTransaction.department_id))
            ).filter(
                SpendTransaction.vendor_id == vendor.id
            ).scalar() or 0
            
            if dept_count == 1:
                # Get the department and total spend
                dept_spend = self.db.query(
                    Department.name,
                    func.sum(SpendTransaction.amount).label('total_spend')
                ).join(SpendTransaction).filter(
                    SpendTransaction.vendor_id == vendor.id
                ).group_by(Department.name).first()
                
                if dept_spend and dept_spend.total_spend >= min_spend_threshold:
                    risk_level = self._calculate_risk(
                        dept_spend.total_spend,
                        vendor.category
                    )
                    
                    results.append({
                        'vendor_id': vendor.id,
                        'vendor_name': vendor.vendor_name,
                        'category': vendor.category,
                        'department': dept_spend.name,
                        'annual_spend': float(dept_spend.total_spend),
                        'risk_level': risk_level,
                        'recommendation': self._generate_recommendation(
                            vendor.vendor_name,
                            dept_spend.name,
                            dept_spend.total_spend
                        )
                    })
        
        return sorted(results, key=lambda x: x['annual_spend'], reverse=True)
    
    def _calculate_risk(self, spend, category):
        """Calculate shadow IT risk level"""
        if category in ['Cloud Infrastructure', 'Monitoring'] and spend > 2500000:
            return 'High'
        elif spend > 1000000:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_recommendation(self, vendor, department, spend):
        """Generate procurement recommendation"""
        return f'{vendor} purchased independently by {department} (₹{spend:,.0f}/year). Central procurement review recommended for potential consolidation or better negotiation.'
