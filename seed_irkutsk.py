from app import create_app
from app.database import get_db
from moduls.user import User
from moduls.venue import Venue
from moduls.event import Event, EventStatus
from moduls.session import Session
from moduls.seat import Seat
from moduls.ticket import Ticket
from moduls.payment import Payment
from moduls.receipt import Receipt
from moduls.review import Review
from moduls.favorite import Favorite
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import string

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def random_price(base=500, variation=300):
    return round(base + random.uniform(-variation, variation), 2)

def generate_receipt_number():
    return 'RCP-' + ''.join(random.choices(string.digits, k=10))

def seed_irkutsk():
    app = create_app()
    with app.app_context():
        db = get_db()
        
        print("🗑️ Очистка старых данных...")
        db.query(Payment).delete()
        db.query(Receipt).delete()
        db.query(Ticket).delete()
        db.query(Review).delete()
        db.query(Favorite).delete()
        db.query(Session).delete()
        db.query(Event).delete()
        db.query(Seat).delete()
        db.query(Venue).delete()
        db.query(User).delete()
        db.commit()
        
        print("👥 Создание пользователей...")
        admin = User(
            email='admin@irk.ru',
            password_hash=generate_password_hash('admin123'),
            full_name='Администратор Иркутск',
            phone='+7 (3952) 00-00-01',
            role='admin',
            is_active=True
        )
        db.add(admin)
        users = [admin]
        for i in range(1, 21):
            user = User(
                email=f'user{i}@irk.ru',
                password_hash=generate_password_hash('user123'),
                full_name=f'Иркутянин {i}',
                phone=f'+7 (3952) 111-22-{i:02d}',
                role='user',
                is_active=True
            )
            db.add(user)
            users.append(user)
        db.commit()
        print(f"✅ Создано {len(users)} пользователей")

        print("🏢 Создание заведений Иркутска...")
        venues_data = [
            {'name': 'Кинотеатр "Баргузин"', 'address': 'ул. Ленина, 15', 'city': 'Иркутск', 'total_seats': 120},
            {'name': 'Кинотеатр "Ленский"', 'address': 'ул. Карла Маркса, 44', 'city': 'Иркутск', 'total_seats': 150},
            {'name': 'Кинотеатр "Cinema 3D"', 'address': 'пр. Маршала Жукова, 36', 'city': 'Иркутск', 'total_seats': 200},
            {'name': 'Кинотеатр "Новый"', 'address': 'ул. Тимирязева, 30', 'city': 'Иркутск', 'total_seats': 180},
            {'name': 'Иркутский академический драматический театр им. Охлопкова', 'address': 'ул. Карла Маркса, 14', 'city': 'Иркутск', 'total_seats': 500},
            {'name': 'Иркутский музыкальный театр им. Загурского', 'address': 'ул. Седова, 29', 'city': 'Иркутск', 'total_seats': 400},
            {'name': 'ТЮЗ им. Вампилова', 'address': 'ул. Ленина, 23', 'city': 'Иркутск', 'total_seats': 300},
            {'name': 'Народный театр "Предместье"', 'address': 'ул. Култукская, 11', 'city': 'Иркутск', 'total_seats': 150},
            {'name': 'Ледовый дворец "Байкал"', 'address': 'ул. Лермонтова, 129', 'city': 'Иркутск', 'total_seats': 2500},
            {'name': 'Дворец спорта "Труд"', 'address': 'ул. Ленина, 48', 'city': 'Иркутск', 'total_seats': 1800},
            {'name': 'Концертный зал "Филармония"', 'address': 'ул. Дзержинского, 2', 'city': 'Иркутск', 'total_seats': 600},
            {'name': 'Молодёжный театр "У Троицы"', 'address': 'ул. 5-й Армии, 8', 'city': 'Иркутск', 'total_seats': 200},
            {'name': 'Стадион "Труд"', 'address': 'ул. Ленина, 48', 'city': 'Иркутск', 'total_seats': 10000},
            {'name': 'Ледовая арена "Байкал"', 'address': 'ул. Байкальская, 269', 'city': 'Иркутск', 'total_seats': 1500},
            {'name': 'Выставочный центр "Сибэкспоцентр"', 'address': 'ул. Байкальская, 253а', 'city': 'Иркутск', 'total_seats': 800},
            {'name': 'Галерея Виктора Бронштейна', 'address': 'ул. Октябрьской Революции, 3', 'city': 'Иркутск', 'total_seats': 200},
        ]
        venues = []
        for vd in venues_data:
            venue = Venue(**vd)
            db.add(venue)
            venues.append(venue)
        db.commit()
        print(f"✅ Создано {len(venues)} заведений")

        print("💺 Генерация мест для залов...")
        for venue in venues:
            rows = random.randint(8, 15)
            seats_per_row = random.randint(10, 20) if venue.total_seats > 150 else random.randint(8, 12)
            for row in range(1, rows+1):
                for seat_num in range(1, seats_per_row+1):
                    seat_type = 'vip' if row <= 2 else 'standard'
                    seat = Seat(
                        venue_id=venue.id,
                        row_number=row,
                        seat_number=seat_num,
                        seat_type=seat_type,
                        is_active=True
                    )
                    db.add(seat)
            actual_seats = rows * seats_per_row
            venue.total_seats = actual_seats
        db.commit()
        print("✅ Места созданы")

        print("🎭 Создание событий (статус APPROVED)...")
        events = []
        for venue in venues:
            name = venue.name.lower()
            if 'кинотеатр' in name:
                category = 'movie'
                titles = ['Чебурашка 2', 'Аватар: Путь воды', 'Оппенгеймер', 'Барби', 'Джон Уик 4', 'Дюна 2', 'Мастер и Маргарита']
            elif 'театр' in name:
                category = 'theater'
                titles = ['Щелкунчик', 'Лебединое озеро', 'Вишнёвый сад', 'Три сестры', 'Ревизор', 'Гамлет']
            elif 'ледовый' in name or 'дворец спорта' in name or 'филармония' in name:
                category = 'concert'
                titles = ['Imagine Dragons', 'Руки Вверх!', 'Баста', 'Любэ', 'Земфира', 'Би-2']
            elif 'стадион' in name or 'арена' in name:
                category = 'sport'
                titles = ['ХК Байкал-Энергия - СКА-Нефтяник', 'ФК Иркутск - Енисей', 'Чемпионат по хоккею с мячом']
            else:
                category = 'exhibition'
                titles = ['Выставка импрессионистов', 'Фотовыставка "Байкал"', 'Ярмарка ремёсел', 'Выставка роботов']
            num_events = random.randint(2, 4)
            used = set()
            for _ in range(num_events):
                available = [t for t in titles if t not in used]
                if not available:
                    break
                title = random.choice(available)
                used.add(title)
                event = Event(
                    venue_id=venue.id,
                    title=title,
                    description=f'Уникальное мероприятие в {venue.name}',
                    category=category,
                    duration_minutes=random.choice([90,120,150]),
                    age_restriction=random.choice([0,6,12,16,18]),
                    poster_url=f'https://picsum.photos/300/200?random={random.randint(1,1000)}',
                    status=EventStatus.APPROVED
                )
                db.add(event)
                events.append(event)
        db.commit()
        print(f"✅ Создано {len(events)} событий")

        print("📅 Генерация сеансов...")
        now = datetime.now()
        sessions = []
        for event in events:
            for i in range(random.randint(3, 6)):
                if i < 2:
                    days_ago = random.randint(30, 330)
                    start = now - timedelta(days=days_ago, hours=random.randint(10, 22))
                else:
                    days_ahead = random.randint(1, 60)
                    start = now + timedelta(days=days_ahead, hours=random.randint(10, 22))
                end = start + timedelta(minutes=event.duration_minutes)
                price = random_price(base=400, variation=200)
                session = Session(
                    event_id=event.id,
                    start_time=start,
                    end_time=end,
                    base_price=price,
                    is_cancelled=False
                )
                db.add(session)
                sessions.append(session)
        db.commit()
        print(f"✅ Создано {len(sessions)} сеансов")

        print("💰 Генерация оплаченных билетов (с платежами и чеками)...")
        tickets = []
        for session in sessions:
            if session.start_time < now:
                venue = session.event.venue
                seats = db.query(Seat).filter_by(venue_id=venue.id, is_active=True).all()
                if not seats:
                    continue
                fill = random.uniform(0.2, 0.7)
                num = int(len(seats) * fill)
                chosen = random.sample(seats, min(num, len(seats)))
                for seat in chosen:
                    user = random.choice(users)
                    paid_at = random_date(session.start_time - timedelta(days=7), session.start_time)
                    ticket = Ticket(
                        user_id=user.id,
                        session_id=session.id,
                        seat_id=seat.id,
                        price_paid=session.base_price,
                        status='paid',
                        paid_at=paid_at
                    )
                    db.add(ticket)
                    db.flush()   # чтобы получить ticket.id
                    payment = Payment(
                        ticket_id=ticket.id,
                        amount=session.base_price,
                        status='succeeded',
                        payment_method='card',
                        paid_at=paid_at
                    )
                    db.add(payment)
                    db.flush()   # чтобы получить payment.id
                    receipt = Receipt(
                        payment_id=payment.id,
                        receipt_number=generate_receipt_number(),
                        sent_to_email=random.choice([True, False])
                    )
                    db.add(receipt)
                    tickets.append(ticket)
        db.commit()
        print(f"✅ Создано {len(tickets)} билетов")

        print("⭐ Генерация отзывов...")
        reviews_cnt = 0
        paid_tickets = [t for t in tickets if t.session and t.session.start_time < datetime.now()]
        # Для контроля уникальности (user_id, event_id) будем использовать множество
        used_pairs = set()
        for ticket in paid_tickets[:200]:
            if random.random() < 0.4:
                key = (ticket.user_id, ticket.session.event_id)
                if key not in used_pairs:
                    existing = db.query(Review).filter_by(user_id=ticket.user_id, event_id=ticket.session.event_id).first()
                    if not existing:
                        review = Review(
                            user_id=ticket.user_id,
                            event_id=ticket.session.event_id,
                            rating=random.randint(3,5),
                            comment=random.choice(['Отлично!', 'Неплохо', 'Восторг!', 'Рекомендую']),
                            is_verified=True
                        )
                        db.add(review)
                        used_pairs.add(key)
                        reviews_cnt += 1
        db.commit()
        print(f"✅ Создано {reviews_cnt} отзывов")

        print("❤️ Избранное...")
        for user in users:
            favs = random.sample(events, min(random.randint(2,5), len(events)))
            for ev in favs:
                if not db.query(Favorite).filter_by(user_id=user.id, event_id=ev.id).first():
                    db.add(Favorite(user_id=user.id, event_id=ev.id))
        db.commit()

        print("\n✅✅✅ БАЗА ДАННЫХ ИРКУТСКА УСПЕШНО ЗАПОЛНЕНА!")
        print(f"   Заведений: {len(venues)}")
        print(f"   Событий: {len(events)} (статус APPROVED)")
        print(f"   Сеансов: {len(sessions)}")
        print(f"   Оплаченных билетов: {len(tickets)}")
        print(f"   Отзывов: {reviews_cnt}")
        print("\n🔑 Учётные записи:")
        print("   admin@irk.ru / admin123")
        print("   user1@irk.ru … user20@irk.ru / user123")

if __name__ == '__main__':
    seed_irkutsk()