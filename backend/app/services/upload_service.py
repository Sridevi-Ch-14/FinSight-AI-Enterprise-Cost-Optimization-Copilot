import pandas as pd
from sqlalchemy.orm import Session
from app.models.models import Department, Vendor, SpendTransaction, Subscription, Contract
from app.utils.vendor_utils import normalize_vendor_name, categorize_vendor
from datetime import datetime
import io

class DataUploadService:
    """Handle CSV uploads and data processing"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_spend_csv(self, file_content: bytes):
        """Process vendor spend CSV"""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Normalize column names
            column_mapping = {
                'PaymentType': 'Payment Type',
                'payment_type': 'Payment Type',
                'payment type': 'Payment Type'
            }
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df.rename(columns={old_col: new_col}, inplace=True)
            
            required_columns = ['Date', 'Department', 'Vendor', 'Category', 'Amount', 'Payment Type']
            if not all(col in df.columns for col in required_columns):
                return {"success": False, "error": f"Missing required columns. Expected: {required_columns}"}
            
            records_added = 0
            
            for _, row in df.iterrows():
                # Get or create department
                dept = self.db.query(Department).filter(
                    Department.name == row['Department']
                ).first()
                if not dept:
                    dept = Department(name=row['Department'])
                    self.db.add(dept)
                    self.db.flush()
                
                # Get or create vendor
                normalized = normalize_vendor_name(row['Vendor'])
                vendor = self.db.query(Vendor).filter(
                    Vendor.normalized_name == normalized
                ).first()
                if not vendor:
                    vendor = Vendor(
                        vendor_name=row['Vendor'],
                        normalized_name=normalized,
                        category=categorize_vendor(normalized)
                    )
                    self.db.add(vendor)
                    self.db.flush()
                
                # Create transaction
                transaction = SpendTransaction(
                    department_id=dept.id,
                    vendor_id=vendor.id,
                    date=pd.to_datetime(row['Date']).date(),
                    amount=float(row['Amount']),
                    spend_type=row['Category'],
                    payment_type=row['Payment Type']
                )
                self.db.add(transaction)
                records_added += 1
            
            self.db.commit()
            return {"success": True, "records_added": records_added}
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def process_subscription_csv(self, file_content: bytes):
        """Process SaaS subscription CSV"""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Normalize column names
            column_mapping = {
                'PlanTier': 'Plan Tier',
                'plan_tier': 'Plan Tier',
                'SeatCount': 'Seat Count',
                'seat_count': 'Seat Count',
                'MonthlyCost': 'Monthly Cost',
                'monthly_cost': 'Monthly Cost',
                'DepartmentOwner': 'Department Owner',
                'department_owner': 'Department Owner'
            }
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df.rename(columns={old_col: new_col}, inplace=True)
            
            required_columns = ['Vendor', 'Plan Tier', 'Seat Count', 'Monthly Cost', 'Department Owner']
            if not all(col in df.columns for col in required_columns):
                return {"success": False, "error": f"Missing required columns. Expected: {required_columns}"}
            
            records_added = 0
            
            for _, row in df.iterrows():
                # Get or create department
                dept = self.db.query(Department).filter(
                    Department.name == row['Department Owner']
                ).first()
                if not dept:
                    dept = Department(name=row['Department Owner'])
                    self.db.add(dept)
                    self.db.flush()
                
                # Get or create vendor
                normalized = normalize_vendor_name(row['Vendor'])
                vendor = self.db.query(Vendor).filter(
                    Vendor.normalized_name == normalized
                ).first()
                if not vendor:
                    vendor = Vendor(
                        vendor_name=row['Vendor'],
                        normalized_name=normalized,
                        category=categorize_vendor(normalized)
                    )
                    self.db.add(vendor)
                    self.db.flush()
                
                # Create subscription
                subscription = Subscription(
                    vendor_id=vendor.id,
                    department_id=dept.id,
                    plan_tier=row['Plan Tier'],
                    seat_count=int(row['Seat Count']),
                    monthly_cost=float(row['Monthly Cost'])
                )
                self.db.add(subscription)
                records_added += 1
            
            self.db.commit()
            return {"success": True, "records_added": records_added}
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
    
    def process_contract_csv(self, file_content: bytes):
        """Process contract renewal CSV"""
        try:
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Normalize column names
            column_mapping = {
                'RenewalDate': 'Renewal Date',
                'renewal_date': 'Renewal Date',
                'AnnualContractValue': 'Annual Contract Value',
                'annual_contract_value': 'Annual Contract Value',
                'AutoRenewFlag': 'Auto-Renew Flag',
                'auto_renew_flag': 'Auto-Renew Flag',
                'AutoRenew': 'Auto-Renew Flag'
            }
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df.rename(columns={old_col: new_col}, inplace=True)
            
            required_columns = ['Vendor', 'Renewal Date', 'Annual Contract Value', 'Auto-Renew Flag']
            if not all(col in df.columns for col in required_columns):
                return {"success": False, "error": f"Missing required columns. Expected: {required_columns}"}
            
            records_added = 0
            
            for _, row in df.iterrows():
                # Get or create vendor
                normalized = normalize_vendor_name(row['Vendor'])
                vendor = self.db.query(Vendor).filter(
                    Vendor.normalized_name == normalized
                ).first()
                if not vendor:
                    vendor = Vendor(
                        vendor_name=row['Vendor'],
                        normalized_name=normalized,
                        category=categorize_vendor(normalized)
                    )
                    self.db.add(vendor)
                    self.db.flush()
                
                # Create contract
                auto_renew = str(row['Auto-Renew Flag']).lower() in ['true', 'yes', '1']
                contract = Contract(
                    vendor_id=vendor.id,
                    renewal_date=pd.to_datetime(row['Renewal Date']).date(),
                    annual_value=float(row['Annual Contract Value']),
                    auto_renew=auto_renew
                )
                self.db.add(contract)
                records_added += 1
            
            self.db.commit()
            return {"success": True, "records_added": records_added}
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
