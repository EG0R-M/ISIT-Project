from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from . import Base

class Hall(Base):
    __tablename__ = "halls"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=True)  # название зала, опционально
    rows = Column(Integer, nullable=False, default=1)
    seats_per_row = Column(Integer, nullable=False, default=1)

    venue = relationship("Venue", back_populates="halls")
    seats = relationship("Seat", back_populates="hall", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="hall", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Hall(id={self.id}, venue_id={self.venue_id}, name={self.name}, rows={self.rows}, seats_per_row={self.seats_per_row})>"