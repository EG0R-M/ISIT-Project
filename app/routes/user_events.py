from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import get_db
from moduls.event import Event, EventStatus
from moduls.venue import Venue
from moduls.hall import Hall
from moduls.seat import Seat
from moduls.session import Session
from moduls.ticket import Ticket
from moduls.user import User
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('user_events', __name__, url_prefix='/my-events')


@bp.route('/')
@login_required
def list_events():
    db = get_db()
    events = db.query(Event).filter_by(user_id=current_user.id).order_by(Event.created_at.desc()).all()

    stats = []
    for event in events:
        total_sessions = db.query(Session).filter_by(event_id=event.id).count()
        paid_tickets = db.query(Ticket).join(Session).filter(
            Session.event_id == event.id,
            Ticket.status == 'paid'
        ).count()
        total_revenue = db.query(func.coalesce(func.sum(Ticket.price_paid), 0)).join(Session).filter(
            Session.event_id == event.id,
            Ticket.status == 'paid'
        ).scalar()
        stats.append({
            'total_sessions': total_sessions,
            'paid_tickets': paid_tickets,
            'total_revenue': float(total_revenue)
        })

    return render_template('user_events/list.html', events=events, stats=stats)


@bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event or event.user_id != current_user.id:
        flash('Мероприятие не найдено.', 'danger')
        return redirect(url_for('user_events.list_events'))

    sessions = db.query(Session).filter_by(event_id=event.id).order_by(Session.start_time).all()

    session_stats = []
    for s in sessions:
        total_seats = db.query(Seat).filter_by(hall_id=s.hall_id, is_active=True).count()
        paid = db.query(Ticket).filter_by(session_id=s.id, status='paid').count()
        pending = db.query(Ticket).filter_by(session_id=s.id, status='pending').count()
        revenue = db.query(func.coalesce(func.sum(Ticket.price_paid), 0)).filter(
            Ticket.session_id == s.id, Ticket.status == 'paid'
        ).scalar()
        tickets = db.query(Ticket).filter_by(session_id=s.id).order_by(Ticket.created_at.desc()).all()
        for t in tickets:
            t.buyer = db.query(User).get(t.user_id)
            t.seat_info = db.query(Seat).get(t.seat_id)
        session_stats.append({
            'session': s,
            'total_seats': total_seats,
            'paid': paid,
            'pending': pending,
            'revenue': float(revenue),
            'tickets': tickets
        })

    return render_template('user_events/detail.html', event=event, session_stats=session_stats)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    db = get_db()
    if request.method == 'POST':
        # ---- Место проведения ----
        venue_name = request.form.get('venue_name', '').strip()
        venue_address = request.form.get('venue_address', '').strip()
        venue_city = request.form.get('venue_city', '').strip()
        
        # Параметры зала
        hall_name = request.form.get('hall_name', '').strip()
        hall_rows = int(request.form.get('hall_rows', 5))
        hall_custom = request.form.get('hall_custom')
        
        if hall_custom:
            custom_seats = request.form.getlist('custom_seats[]')
            seats_per_row_list = []
            for i, val in enumerate(custom_seats[:hall_rows]):
                try:
                    seats = int(val)
                    if seats < 1:
                        seats = 1
                except (ValueError, TypeError):
                    seats = 10
                seats_per_row_list.append(seats)
            # Добиваем до hall_rows если не хватает
            while len(seats_per_row_list) < hall_rows:
                seats_per_row_list.append(10)
            hall_seats_per_row = max(seats_per_row_list)
        else:
            hall_seats_per_row = int(request.form.get('hall_seats_per_row', 10))
            seats_per_row_list = None
        
        if not venue_name or not venue_city:
            flash('Название заведения и город обязательны.', 'danger')
            return redirect(url_for('user_events.create'))
        
        # Ищем или создаём место
        venue = db.query(Venue).filter_by(name=venue_name, city=venue_city).first()
        if not venue:
            venue = Venue(
                name=venue_name,
                address=venue_address or 'Адрес не указан',
                city=venue_city,
                total_seats=0
            )
            db.add(venue)
            db.flush()
        
        # ---- Создаём зал и места ----
        hall = Hall(
            venue_id=venue.id,
            name=hall_name or 'Основной зал',
            rows=hall_rows,
            seats_per_row=hall_seats_per_row
        )
        db.add(hall)
        db.flush()
        
        total_seats = 0
        for row in range(1, hall_rows + 1):
            seats_in_row = seats_per_row_list[row - 1] if seats_per_row_list else hall_seats_per_row
            total_seats += seats_in_row
            for seat_num in range(1, seats_in_row + 1):
                seat_type = 'vip' if row <= 2 else 'standard'
                seat = Seat(
                    hall_id=hall.id,
                    row_number=row,
                    seat_number=seat_num,
                    seat_type=seat_type,
                    is_active=True
                )
                db.add(seat)
        
        venue.total_seats = total_seats
        
        # ---- Основные данные мероприятия ----
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category')
        duration = request.form.get('duration_minutes')
        age = request.form.get('age_restriction')
        poster = request.form.get('poster_url', '').strip()
        
        if not title or not category:
            flash('Название мероприятия и категория обязательны.', 'danger')
            return redirect(url_for('user_events.create'))
        
        event = Event(
            title=title,
            description=description,
            category=category,
            venue_id=venue.id,
            user_id=current_user.id,
            duration_minutes=int(duration) if duration else None,
            age_restriction=int(age) if age else 0,
            poster_url=poster if poster else None,
            status=EventStatus.PENDING
        )
        db.add(event)
        db.flush()   # чтобы получить event.id
        
        # ---- Сеансы (даты и цены) ----
        starts = request.form.getlist('sessions_start[]')
        ends = request.form.getlist('sessions_end[]')
        prices = request.form.getlist('sessions_price[]')
        
        for i in range(len(starts)):
            start_str = starts[i].strip()
            if not start_str:
                continue
            try:
                start = datetime.fromisoformat(start_str)
            except ValueError:
                flash(f'Неверный формат даты в сеансе {i+1}', 'danger')
                return redirect(url_for('user_events.create'))
            
            end = None
            end_str = ends[i].strip() if i < len(ends) else ''
            if end_str:
                try:
                    end = datetime.fromisoformat(end_str)
                except ValueError:
                    flash(f'Неверный формат даты окончания в сеансе {i+1}', 'danger')
                    return redirect(url_for('user_events.create'))
            elif event.duration_minutes:
                end = start + timedelta(minutes=event.duration_minutes)
            else:
                end = start + timedelta(hours=2)  # значение по умолчанию
            
            try:
                price = float(prices[i])
            except (ValueError, TypeError):
                price = 0.0
            
            session = Session(
                event_id=event.id,
                hall_id=hall.id,           # <-- привязка к залу
                start_time=start,
                end_time=end,
                base_price=price,
                is_cancelled=False
            )
            db.add(session)
        
        db.commit()
        flash('Мероприятие и сеансы отправлены на модерацию.', 'success')
        return redirect(url_for('profile.dashboard'))
    
    # GET: отображаем пустую форму
    return render_template('user_events/create.html')