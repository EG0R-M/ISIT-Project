from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    payment = relationship("Payment", back_populates="receipt")
    
    def __repr__(self):
        return f"<Receipt(id={self.id}, receipt_number={self.receipt_number}, sent_to_email={self.sent_to_email})>"