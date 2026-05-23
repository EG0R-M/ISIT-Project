from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='unique_review_per_user_event'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    user = relationship("User", back_populates="reviews")
    event = relationship("Event", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, event_id={self.event_id}, rating={self.rating})>"