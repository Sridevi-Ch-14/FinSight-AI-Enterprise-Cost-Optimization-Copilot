from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.config.database import Base

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    
    spend_transactions = relationship("SpendTransaction", back_populates="department")
    subscriptions = relationship("Subscription", back_populates="department")

class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(255), unique=True, nullable=False)
    normalized_name = Column(String(255), index=True)
    category = Column(String(100))
    benchmark_cost = Column(Float)
    risk_score = Column(Float, default=0.0)
    
    spend_transactions = relationship("SpendTransaction", back_populates="vendor")
    subscriptions = relationship("Subscription", back_populates="vendor")
    contracts = relationship("Contract", back_populates="vendor")
    recommendations = relationship("Recommendation", back_populates="vendor")

class SpendTransaction(Base):
    __tablename__ = "spend_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    spend_type = Column(String(50))
    payment_type = Column(String(50))
    
    department = relationship("Department", back_populates="spend_transactions")
    vendor = relationship("Vendor", back_populates="spend_transactions")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    department_id = Column(Integer, ForeignKey("departments.id"))
    plan_tier = Column(String(100))
    seat_count = Column(Integer)
    monthly_cost = Column(Float)
    
    vendor = relationship("Vendor", back_populates="subscriptions")
    department = relationship("Department", back_populates="subscriptions")

class Contract(Base):
    __tablename__ = "contracts"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    contract_name = Column(String(255))
    renewal_date = Column(Date, nullable=False)
    annual_value = Column(Float, nullable=False)
    auto_renew = Column(Boolean, default=True)
    department_owner = Column(String(255))
    
    vendor = relationship("Vendor", back_populates="contracts")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    recommendation_type = Column(String(100))
    projected_savings = Column(Float)
    rationale = Column(Text)
    risk_level = Column(String(20))
    alternative_vendor = Column(String(255))
    feature_parity = Column(Text)
    
    vendor = relationship("Vendor", back_populates="recommendations")

class ChatQuery(Base):
    __tablename__ = "chat_queries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    generated_sql = Column(Text)
    result = Column(Text)
    session_id = Column(String(64), index=True, nullable=True)   # conversational memory
    explanation = Column(Text, nullable=True)                    # plain-English summary
    created_at = Column(DateTime, default=datetime.utcnow)
