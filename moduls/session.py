from sqlalchemy import Column, Integer, DateTime, Boolean, Numeric, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)
    is_cancelled = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    event = relationship("Event", back_populates="sessions")
    tickets = relationship("Ticket", back_populates="session", cascade="all, delete-orphan")
    
    # Индексы
    __table_args__ = (
        Index('idx_sessions_start_time', 'start_time'),
        Index('idx_sessions_event_id', 'event_id'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, event_id={self.event_id}, start_time={self.start_time})>"