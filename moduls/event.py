from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base
import enum

class EventStatus(enum.Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)   # кто создал
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    poster_url = Column(String(500))
    duration_minutes = Column(Integer)
    age_restriction = Column(Integer, default=0)
    status = Column(Enum(EventStatus), default=EventStatus.PENDING, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    venue = relationship("Venue", back_populates="events")
    creator = relationship("User", foreign_keys=[user_id], backref="created_events")   # кто создал мероприятие
    sessions = relationship("Session", back_populates="event", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="event", cascade="all, delete-orphan")
    favorited_by = relationship("Favorite", back_populates="event", cascade="all, delete-orphan")   # ← добавить