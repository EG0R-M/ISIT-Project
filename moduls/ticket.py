from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    seat_id = Column(Integer, ForeignKey("seats.id", ondelete="CASCADE"), nullable=False)
    price_paid = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), default="pending")  # pending / paid / cancelled / expired
    booking_expires_at = Column(DateTime)
    qr_code = Column(String(500))
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Уникальное ограничение: место не может быть продано дважды на один сеанс
    __table_args__ = (
        UniqueConstraint('session_id', 'seat_id', name='unique_seat_per_session'),
        Index('idx_tickets_user_id', 'user_id'),
        Index('idx_tickets_session_id', 'session_id'),
        Index('idx_tickets_status', 'status'),
    )
    
    # Связи
    user = relationship("User", back_populates="tickets")
    session = relationship("Session", back_populates="tickets")
    seat = relationship("Seat", back_populates="tickets")
    payment = relationship("Payment", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, user_id={self.user_id}, status={self.status})>"