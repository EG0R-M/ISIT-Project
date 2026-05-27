from app import create_app
from app.database import get_db
from moduls.user import User
from moduls.venue import Venue
from moduls.event import Event
from moduls.session import Session
from moduls.seat import Seat
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # 1. Создаём тестового админа (если нет)
        admin = db.query(User).filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                password_hash=generate_password_hash('admin123'),
                full_name='Администратор',
                phone='+7 (999) 123-45-67',
                role='admin',
                is_active=True
            )
            db.add(admin)
            print('Администратор создан: admin@example.com / admin123')
        
        # 2. Создаём тестового пользователя
        user = db.query(User).filter_by(email='user@example.com').first()
        if not user:
            user = User(
                email='user@example.com',
                password_hash=generate_password_hash('user123'),
                full_name='Тестовый Пользователь',
                phone='+7 (999) 987-65-43',
                role='user',
                is_active=True
            )
            db.add(user)
            print('Пользователь создан: user@example.com / user123')
        
        db.commit()
        
        # 3. Создаём площадки (venues)
        venues = [
            Venue(name='Крокус Сити Холл', address='ул. Международная, 20', city='Москва', total_seats=2000),
            Venue(name='Большой Театр', address='Театральная пл., 1', city='Москва', total_seats=1500),
            Venue(name='Кинотеатр Октябрь', address='ул. Тверская, 22', city='Москва', total_seats=500),
            Venue(name='Ледовый Дворец', address='ул. Летняя, 10', city='Санкт-Петербург', total_seats=3000),
            Venue(name='Стендап Клуб', address='ул. Пушкина, 15', city='Москва', total_seats=150),
        ]
        
        for v in venues:
            existing = db.query(Venue).filter_by(name=v.name).first()
            if not existing:
                db.add(v)
                print(f'Площадка добавлена: {v.name}')
        
        db.commit()
        
        # 4. Создаём мероприятия (events)
        events = [
            Event(
                title='Imagine Dragons - Концерт',
                description='Грандиозный концерт популярной рок-группы Imagine Dragons',
                category='concert',
                venue_id=1,
                duration_minutes=120,
                age_restriction=12,
                poster_url='https://via.placeholder.com/300x200?text=Imagine+Dragons'
            ),
            Event(
                title='Щелкунчик',
                description='Волшебный балет Петра Чайковского',
                category='theater',
                venue_id=2,
                duration_minutes=150,
                age_restriction=6,
                poster_url='https://via.placeholder.com/300x200?text=Nutcracker'
            ),
            Event(
                title='Аватар: Путь воды',
                description='Фантастический фильм Джеймса Кэмерона',
                category='movie',
                venue_id=3,
                duration_minutes=192,
                age_restriction=12,
                poster_url='https://via.placeholder.com/300x200?text=Avatar'
            ),
            Event(
                title='ЦСКА - Спартак',
                description='Дерби двух главных клубов Москвы',
                category='sport',
                venue_id=4,
                duration_minutes=120,
                age_restriction=0,
                poster_url='https://via.placeholder.com/300x200?text=CSKA+Spartak'
            ),
            Event(
                title='Стендап с Павлом Воле',
                description='Новое юмористическое шоу',
                category='concert',
                venue_id=5,
                duration_minutes=90,
                age_restriction=18,
                poster_url='https://via.placeholder.com/300x200?text=Standup'
            ),
            Event(
                title='Выставка импрессионистов',
                description='Шедевры Моне, Ренуара и Дега',
                category='exhibition',
                venue_id=1,
                duration_minutes=180,
                age_restriction=0,
                poster_url='https://via.placeholder.com/300x200?text=Impressionists'
            ),
            Event(
                title='Гарри Поттер и проклятое дитя',
                description='Спектакль по мотивам книги Дж.К. Роулинг',
                category='theater',
                venue_id=2,
                duration_minutes=180,
                age_restriction=12,
                poster_url='https://via.placeholder.com/300x200?text=Harry+Potter'
            ),
            Event(
                title='Руки Вверх!',
                description='Новогодний концерт легендарной группы',
                category='concert',
                venue_id=1,
                duration_minutes=150,
                age_restriction=6,
                poster_url='https://via.placeholder.com/300x200?text=Ruki+Vverh'
            ),
        ]
        
        for e in events:
            existing = db.query(Event).filter_by(title=e.title).first()
            if not existing:
                db.add(e)
                print(f'Мероприятие добавлено: {e.title}')
        
        db.commit()
        
        # 5. Создаём сеансы для каждого мероприятия
        now = datetime.now()
        
        for event in db.query(Event).all():
            # Проверяем, есть ли уже сеансы
            existing_sessions = db.query(Session).filter_by(event_id=event.id).first()
            if existing_sessions:
                continue
            
            # Создаём сеансы на ближайшие дни
            for days in range(1, 6):
                session = Session(
                    event_id=event.id,
                    start_time=now + timedelta(days=days, hours=19),
                    end_time=now + timedelta(days=days, hours=19) + timedelta(minutes=event.duration_minutes),
                    base_price=500 + event.id * 100,
                    is_cancelled=False
                )
                db.add(session)
                print(f'Сеанс добавлен: {event.title} на {session.start_time.strftime("%d.%m.%Y %H:%M")}')
        
        db.commit()
        
        # 6. Создаём места для каждой площадки
        for venue in db.query(Venue).all():
            existing_seats = db.query(Seat).filter_by(venue_id=venue.id).first()
            if existing_seats:
                continue
            
            # Создаём места: ряды 1-10, в каждом по 10-20 мест
            for row in range(1, 11):
                seats_in_row = 15 if row <= 5 else 10  # VIP-ряды ближе к сцене
                for seat_num in range(1, seats_in_row + 1):
                    seat_type = 'vip' if row <= 3 else 'standard'
                    seat = Seat(
                        venue_id=venue.id,
                        row_number=row,
                        seat_number=seat_num,
                        seat_type=seat_type,
                        is_active=True
                    )
                    db.add(seat)
            print(f'Созданы места для площадки: {venue.name}')
        
        db.commit()
        
        print('\n✅ База данных успешно заполнена тестовыми данными!')
        print('\n📝 Тестовые учетные записи:')
        print('   Админ: admin@example.com / admin123')
        print('   Пользователь: user@example.com / user123')

if __name__ == '__main__':
    seed_database()