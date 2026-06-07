from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from . import Base

class Seat(Base):
    __tablename__ = "seats"
    
    id = Column(Integer, primary_key=True, index=True)
    hall_id = Column(Integer, ForeignKey("halls.id", ondelete="CASCADE"), nullable=False)
    row_number = Column(Integer, nullable=False)
    seat_number = Column(Integer, nullable=False)
    seat_type = Column(String(50), default="standard")  # standard / vip / disabled
    is_active = Column(Boolean, default=True)
    
    # Уникальное ограничение: в одном зале нет двух одинаковых мест
    __table_args__ = (
        UniqueConstraint('hall_id', 'row_number', 'seat_number', name='unique_seat_per_hall'),
    )
    
    # Связи
    hall = relationship("Hall", back_populates="seats")
    tickets = relationship("Ticket", back_populates="seat")
    
    def __repr__(self):
        return f"<Seat(id={self.id}, hall_id={self.hall_id}, row={self.row_number}, seat={self.seat_number})>"