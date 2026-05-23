from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime  # добавили DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, unique=True)
    receipt_number = Column(String(100), nullable=False, unique=True)
    pdf_url = Column(String(500))
    sent_to_email = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())   # теперь DateTime определён
    
    payment = relationship("Payment", back_populates="receipt")