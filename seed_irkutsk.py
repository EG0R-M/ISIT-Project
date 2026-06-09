import json
import os
from app import create_app
from app.database import get_db
from moduls.user import User
from moduls.venue import Venue
from moduls.hall import Hall          # <-- добавлен импорт
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

        # Удаляем таблицы в порядке зависимостей (от дочерних к родительским)
        print("Очистка старых данных...")
        db.query(Seat).delete()
        db.query(Session).delete()
        db.query(Hall).delete()        # <-- добавлено
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
                total_seats=0
            )
            db.add(venue)
            db.flush()  # получаем id
            venues[vd['name']] = venue
        db.commit()
        print(f"✅ Загружено {len(venues)} заведений")

        print("💺 Генерация залов и мест...")
        for vd in venues_data:
            venue = venues[vd['name']]
            halls_data = vd.get('halls', [])
            if not halls_data:
                halls_data = [{'name': 'Основной зал', 'rows': 5, 'seats_per_row': 10}]
            
            total_seats_venue = 0
            for hd in halls_data:
                hall = Hall(
                    venue_id=venue.id,
                    name=hd.get('name'),
                    rows=hd['rows'],
                    seats_per_row=hd['seats_per_row']
                )
                db.add(hall)
                db.flush()
                # Генерация мест в зале
                for row in range(1, hall.rows+1):
                    for seat_num in range(1, hall.seats_per_row+1):
                        seat_type = 'vip' if row <= 2 else 'standard'
                        seat = Seat(
                            hall_id=hall.id,
                            row_number=row,
                            seat_number=seat_num,
                            seat_type=seat_type,
                            is_active=True
                        )
                        db.add(seat)
                total_seats_venue += hall.rows * hall.seats_per_row
            venue.total_seats = total_seats_venue
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
            unique_key = f"{ed['title']}|{ed['venue_name']}"
            events[unique_key] = event
        db.commit()
        print(f"✅ Загружено {len(events)} событий")

        print("📅 Загрузка сеансов из sessions.json...")
        sessions_data = load_json('sessions.json')
        sessions_count = 0
        for sd in sessions_data:
            unique_key = f"{sd['event_title']}|{sd['venue_name']}"
            event = events.get(unique_key)
            if not event:
                print(f"⚠️ Событие '{sd['event_title']}' не найдено. Сеанс пропущен.")
                continue
            
            # Ищем зал по названию (если указано) или берём первый
            hall = None
            if 'hall_name' in sd and sd['hall_name']:
                hall = db.query(Hall).filter_by(venue_id=event.venue_id, name=sd['hall_name']).first()
                if not hall:
                    print(f"⚠️ Зал '{sd['hall_name']}' не найден для площадки {event.venue.name}. Сеанс пропущен.")
                    continue
            else:
                # Если hall_name не указан, берём первый зал (для обратной совместимости)
                hall = db.query(Hall).filter_by(venue_id=event.venue_id).first()
                if not hall:
                    print(f"⚠️ Нет залов для заведения {event.venue.name}, сеанс пропущен.")
                    continue
            
            start = datetime.fromisoformat(sd['start_time'])
            if 'end_time' in sd and sd['end_time']:
                end = datetime.fromisoformat(sd['end_time'])
            else:
                end = start + timedelta(minutes=event.duration_minutes)
            
            session = Session(
                event_id=event.id,
                hall_id=hall.id,
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