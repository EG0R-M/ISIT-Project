from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()






# Импортируем все модели для создания таблиц
from .user import User
from .venue import Venue
from .event import Event
from .seat import Seat
from .session import Session
from .ticket import Ticket
from .payment import Payment
from .receipt import Receipt
from .review import Review
from .favorite import Favorite
# Функция для подключения к БД
def init_db(database_url="sqlite:///booking.db"):
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal, engine

__all__ = [
    "Base",
    "User",
    "Venue", 
    "Event",
    "Seat",
    "Session",
    "Ticket",
    "Payment",
    "Receipt",
    "Review",
    "init_db"
]