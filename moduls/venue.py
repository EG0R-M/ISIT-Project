from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base

class Venue(Base):
    __tablename__ = "venues"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    description = Column(Text)
    total_seats = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    # Связи
    events = relationship("Event", back_populates="venue", cascade="all, delete-orphan")
    halls = relationship("Hall", back_populates="venue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Venue(id={self.id}, name={self.name}, city={self.city})>"