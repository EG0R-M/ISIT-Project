from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import get_db
from moduls.event import Event, EventStatus
from moduls.venue import Venue
from moduls.session import Session
from datetime import datetime, timedelta

bp = Blueprint('user_events', __name__, url_prefix='/my-events')

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    db = get_db()
    if request.method == 'POST':
        # ---- Место проведения ----
        venue_name = request.form.get('venue_name', '').strip()
        venue_address = request.form.get('venue_address', '').strip()
        venue_city = request.form.get('venue_city', '').strip()
        
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