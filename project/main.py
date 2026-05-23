# main.py
from moduls import init_db, User, Venue, Event

# Инициализация БД (SQLite для примера)
SessionLocal, engine = init_db("sqlite:///booking.db")
db = SessionLocal()

# Создание тестовых данных
new_venue = Venue(
    name="Кинотеатр Октябрь",
    address="ул. Тверская, 22",
    city="Москва",
    total_seats=150
)

db.add(new_venue)
db.commit()

# Запрос
venue = db.query(Venue).filter_by(name="Кинотеатр Октябрь").first()
print(venue)

db.close()