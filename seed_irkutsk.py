import json
import os
from app import create_app
from app.database import get_db
from moduls.user import User
from moduls.venue import Venue
from moduls.event import Event, EventStatus
from moduls.session import Session
from moduls.seat import Seat
from werkzeug.security import generate_password_hash

# Путь к папке с JSON-файлами (можно указать свой)
JSON_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_json(filename):
    with open(os.path.join(JSON_DIR, filename), 'r', encoding='utf-8') as f:
        return json.load(f)

def seed_from_json():
    app = create_app()
    with app.app_context():
        db = get_db()

        print("🗑 Очистка старых данных...")
        # Удаляем таблицы в порядке зависимостей (от дочерних к родительским)
        db.query(Seat).delete()
        db.query(Session).delete()
        db.query(Event).delete()
        db.query(Venue).delete()
        db.query(User).delete()
        db.commit()

        print("👥 Создание пользователей...")
        # Администратор
        admin = User(
            email='admin@irk.ru',
            password_hash=generate_password_hash('admin123'),
            full_name='Администратор',
            phone='+7 (3952) 00-00-01',
            role='admin',
            is_active=True
        )
        db.add(admin)
        # Несколько обычных пользователей для тестов
        users = [admin]
        for i in range(1, 6):
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
        print(f"✅ Создано {len(users)} пользователей (включая админа)")

        print("🏢 Загрузка заведений из venues.json...")
        venues_data = load_json('venues.json')
        venues = {}
        for vd in venues_data:
            venue = Venue(
                name=vd['name'],
                address=vd['address'],
                city=vd['city'],
                total_seats=vd.get('rows', 0) * vd.get('seats_per_row', 0)
            )
            db.add(venue)
            db.flush()  # получаем id
            venues[vd['name']] = venue
        db.commit()
        print(f"✅ Загружено {len(venues)} заведений")

        print("💺 Генерация мест для залов...")
        for vd in venues_data:
            venue = venues[vd['name']]
            rows = vd.get('rows', 5)
            seats_per_row = vd.get('seats_per_row', 10)
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
            # Обновляем total_seats в venue
            venue.total_seats = rows * seats_per_row
        db.commit()
        print("✅ Места созданы")

        print("🎭 Загрузка событий из events.json...")
        events_data = load_json('events.json')
        events = {}
        for ed in events_data:
            venue = venues.get(ed['venue_name'])
            if not venue:
                print(f"⚠️ Заведение '{ed['venue_name']}' не найдено. Событие '{ed['title']}' пропущено.")
                continue
            # Преобразуем строку статуса в enum
            status_str = ed.get('status', 'approved')
            if status_str == 'approved':
                status = EventStatus.APPROVED
            elif status_str == 'pending':
                status = EventStatus.PENDING
            else:
                status = EventStatus.REJECTED
            event = Event(
                venue_id=venue.id,
                title=ed['title'],
                description=ed.get('description', ''),
                category=ed['category'],
                duration_minutes=ed.get('duration_minutes'),
                age_restriction=ed.get('age_restriction', 0),
                poster_url=ed.get('poster_url', ''),
                status=status,
                user_id=admin.id  # создано админом
            )
            db.add(event)
            db.flush()
            events[ed['title']] = event
        db.commit()
        print(f"✅ Загружено {len(events)} событий")

        print("📅 Загрузка сеансов из sessions.json...")
        sessions_data = load_json('sessions.json')
        sessions_count = 0
        for sd in sessions_data:
            event = events.get(sd['event_title'])
            if not event:
                print(f"⚠️ Событие '{sd['event_title']}' не найдено. Сеанс пропущен.")
                continue
            start = datetime.fromisoformat(sd['start_time'])
            # Если end_time не указан, вычисляем по длительности события
            if 'end_time' in sd and sd['end_time']:
                end = datetime.fromisoformat(sd['end_time'])
            else:
                end = start + timedelta(minutes=event.duration_minutes)
            session = Session(
                event_id=event.id,
                start_time=start,
                end_time=end,
                base_price=sd['base_price'],
                is_cancelled=False
            )
            db.add(session)
            sessions_count += 1
        db.commit()
        print(f"✅ Загружено {sessions_count} сеансов")

        print("\n✅✅✅ БАЗА ДАННЫХ УСПЕШНО ЗАПОЛНЕНА ИЗ JSON-ФАЙЛОВ!")
        print(f"   Пользователей: {len(users)}")
        print(f"   Заведений: {len(venues)}")
        print(f"   Событий: {len(events)}")
        print(f"   Сеансов: {sessions_count}")
        print("\n🔑 Учётные записи:")
        print("   admin@irk.ru / admin123")
        for i in range(1, 6):
            print(f"   user{i}@irk.ru / user123")

if __name__ == '__main__':
    from datetime import datetime, timedelta  # импорт внутри, чтобы не было ошибок в глобальной области
    seed_from_json()