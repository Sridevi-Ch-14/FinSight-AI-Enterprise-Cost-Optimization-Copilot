from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Vendor, SpendTransaction, Subscription, Contract, Recommendation, Department
from app.utils.alternatives import get_alternatives, get_benchmark_price
from datetime import datetime, timedelta

class RecommendationEngine:
    """Generate conservative, evidence-based cost optimization recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_all_recommendations(self):
        """Generate all types of recommendations"""
        self.db.query(Recommendation).delete()
        
        self.detect_vendor_consolidation()
        self.detect_contract_renewals()
        self.detect_subscription_optimization()
        
        self.db.commit()
    
    def detect_vendor_consolidation(self):
        """Detect overlapping vendors - conservative approach"""
        # Get categories with multiple DISTINCT vendors
        categories = self.db.query(
            Vendor.category,
            func.count(func.distinct(Vendor.id)).label('vendor_count'),
            func.sum(SpendTransaction.amount).label('total_spend')
        ).join(SpendTransaction).filter(
            Vendor.category.isnot(None)
        ).group_by(Vendor.category).having(
            func.count(func.distinct(Vendor.id)) > 1
        ).all()
        
        for category, vendor_count, total_spend in categories:
            if vendor_count < 2:
                continue
            
            # Get actual distinct vendors in this category
            vendors_in_category = self.db.query(Vendor).join(SpendTransaction).filter(
                Vendor.category == category
            ).distinct().all()
            
            # Calculate spend per vendor
            vendor_spends = []
            for vendor in vendors_in_category:
                spend = self.db.query(func.sum(SpendTransaction.amount)).filter(
                    SpendTransaction.vendor_id == vendor.id
                ).scalar() or 0
                vendor_spends.append((vendor, spend))
            
            vendor_spends.sort(key=lambda x: x[1], reverse=True)
            
            if len(vendor_spends) < 2:
                continue
            
            primary_vendor = vendor_spends[0][0]
            vendor_names = [v.vendor_name for v, _ in vendor_spends]
            vendor_normalized = [v.normalized_name for v, _ in vendor_spends]
            
            # Conservative savings: only 10-15% of secondary spend
            secondary_spend = sum(spend for v, spend in vendor_spends[1:])
            
            # Category-specific logic
            rationale = ''
            savings_rate = 0.10
            risk_level = 'Medium'
            
            if category == 'Communication':
                if any('teams' in v for v in vendor_normalized):
                    rationale = f'Multiple communication tools detected ({len(vendor_spends)} vendors: {", ".join(vendor_names)}). Microsoft Teams provides integrated chat and meetings. Procurement may review license allocation.'
                    savings_rate = 0.12
                else:
                    rationale = f'{len(vendor_spends)} communication platforms detected ({", ".join(vendor_names)}). Consider standardizing to reduce complexity.'
                    savings_rate = 0.10
            
            elif category == 'Cloud Infrastructure':
                rationale = f'Multi-cloud environment detected ({", ".join(vendor_names)}). Focus on FinOps optimization (Reserved Instances, Savings Plans) rather than migration.'
                savings_rate = 0.08
                risk_level = 'High'
            
            elif category == 'Project Management':
                rationale = f'{len(vendor_spends)} project management tools in use ({", ".join(vendor_names)}). Standardization may improve collaboration and reduce training costs.'
                savings_rate = 0.12
            
            elif category == 'Design Tools':
                rationale = f'Multiple design tools detected ({", ".join(vendor_names)}). Review enterprise licensing consolidation opportunities.'
                savings_rate = 0.10
            
            else:
                rationale = f'{len(vendor_spends)} vendors in {category} category ({", ".join(vendor_names)}). Procurement review recommended.'
                savings_rate = 0.10
            
            projected_savings = secondary_spend * savings_rate
            
            # Only create recommendation if savings > threshold
            if projected_savings > 50000:
                rec = Recommendation(
                    vendor_id=primary_vendor.id,
                    recommendation_type='consolidation',
                    projected_savings=projected_savings,
                    rationale=rationale,
                    risk_level=risk_level,
                    alternative_vendor=None,
                    feature_parity=f'Review opportunity: {len(vendor_spends)} vendors, ₹{total_spend:,.0f} combined annual spend'
                )
                self.db.add(rec)
    
    def detect_contract_renewals(self):
        """Alert on upcoming renewals - no hallucinated alternatives"""
        upcoming = datetime.now().date() + timedelta(days=90)
        contracts = self.db.query(Contract).filter(
            Contract.renewal_date <= upcoming,
            Contract.renewal_date >= datetime.now().date()
        ).all()
        
        for contract in contracts:
            vendor = self.db.query(Vendor).filter(Vendor.id == contract.vendor_id).first()
            if not vendor:
                continue
            
            days_until = (contract.renewal_date - datetime.now().date()).days
            
            # Conservative: just flag the renewal, don't hallucinate savings
            rationale = f'Contract renewal in {days_until} days (₹{contract.annual_value:,.0f}/year). '
            
            if contract.auto_renew:
                rationale += 'Auto-renew enabled. Review recommended before renewal date.'
            else:
                rationale += 'Renegotiation opportunity. Consider market rate benchmarking.'
            
            # Only suggest alternatives if they exist in our knowledge base
            alternatives = get_alternatives(vendor.normalized_name)
            projected_savings = 0
            risk_level = 'Low'
            alt_vendor = None
            feature_parity = 'Contract renewal review recommended'
            
            if alternatives and vendor.category != 'Cloud Infrastructure':
                alt = alternatives[0]
                # Conservative: max 10% savings estimate for renewals
                projected_savings = contract.annual_value * 0.10
                alt_vendor = alt['name']
                feature_parity = f'Alternative option: {alt["name"]} - {alt["feature_parity"]}'
                risk_level = alt['risk_level']
            
            rec = Recommendation(
                vendor_id=vendor.id,
                recommendation_type='contract_renewal',
                projected_savings=projected_savings,
                rationale=rationale,
                risk_level=risk_level,
                alternative_vendor=alt_vendor,
                feature_parity=feature_parity
            )
            self.db.add(rec)
    
    def detect_subscription_optimization(self):
        """Detect over-provisioned licenses - ONE recommendation per vendor"""
        # Aggregate ALL subscriptions by vendor (sum seats and costs)
        aggregated = self.db.query(
            Subscription.vendor_id,
            func.sum(Subscription.seat_count).label('total_seats'),
            func.sum(Subscription.monthly_cost).label('total_monthly_cost')
        ).group_by(
            Subscription.vendor_id
        ).all()
        
        for vendor_id, total_seats, total_monthly_cost in aggregated:
            vendor = self.db.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                continue
            
            annual_cost = total_monthly_cost * 12
            
            # Skip small subscriptions
            if annual_cost < 500000:
                continue
            
            # Check if vendor has premium tiers
            has_premium = self.db.query(Subscription).filter(
                Subscription.vendor_id == vendor_id,
                Subscription.plan_tier.in_(['Enterprise', 'Premium', 'Pro'])
            ).first() is not None
            
            # Confidence scoring based on seat count
            if total_seats > 500:
                confidence = 'High'
                savings_rate = 0.10 if has_premium else 0.08
            elif total_seats >= 200:
                confidence = 'Medium'
                savings_rate = 0.08 if has_premium else 0.06
            else:
                confidence = 'Low'
                savings_rate = 0.05
            
            projected_savings = annual_cost * savings_rate
            
            # Single rationale per vendor
            rationale = f'{vendor.vendor_name} (Total seats: {total_seats:,} across departments, ₹{annual_cost:,.0f}/year). '
            if has_premium:
                rationale += 'Review premium tier utilization and seat allocation for optimization opportunities.'
            else:
                rationale += 'Audit active seat usage to identify unused licenses.'
            
            rec = Recommendation(
                vendor_id=vendor.id,
                recommendation_type='subscription_optimization',
                projected_savings=projected_savings,
                rationale=rationale,
                risk_level=confidence,
                alternative_vendor=None,
                feature_parity=f'{confidence} confidence recommendation'
            )
            self.db.add(rec)
