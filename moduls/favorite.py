from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'event_id', name='unique_user_event_favorite'),
    )
    
    user = relationship("User", back_populates="favorites")
    event = relationship("Event", back_populates="favorited_by")