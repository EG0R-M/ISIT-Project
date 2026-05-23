from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, unique=True)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending")  # pending / succeeded / failed / refunded
    payment_method = Column(String(50), default="card")  # card / cash
    transaction_id = Column(String(255))
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Индексы
    __table_args__ = (
        Index('idx_payments_ticket_id', 'ticket_id'),
        Index('idx_payments_status', 'status'),
    )
    
    # Связи
    ticket = relationship("Ticket", back_populates="payment")
    receipt = relationship("Receipt", back_populates="payment", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, ticket_id={self.ticket_id}, status={self.status}, amount={self.amount})>"