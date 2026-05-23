from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)  # movie / theater / concert / sport
    poster_url = Column(String(500))
    duration_minutes = Column(Integer)
    age_restriction = Column(Integer, default=0)  # 0+, 6+, 12+, 16+, 18+
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    venue = relationship("Venue", back_populates="events")
    sessions = relationship("Session", back_populates="event", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="event", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, category={self.category})>"