from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.database import get_db
from moduls.user import User
from moduls.event import Event
from moduls.venue import Venue
from moduls.ticket import Ticket

bp = Blueprint('admin', __name__)

@bp.route('/')
@login_required
def index():
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    users_count = db.query(User).count()
    events_count = db.query(Event).count()
    tickets_count = db.query(Ticket).count()
    return render_template('admin/index.html', 
                          users_count=users_count, 
                          events_count=events_count, 
                          tickets_count=tickets_count)

@bp.route('/events')
@login_required
def events():
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    events = db.query(Event).order_by(Event.created_at.desc()).all()
    return render_template('admin/events.html', events=events)

@bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    venues = db.query(Venue).all()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        venue_id = request.form['venue_id']
        duration_minutes = int(request.form['duration_minutes'])
        age_restriction = int(request.form['age_restriction'])
        poster_url = request.form.get('poster_url')
        
        event = Event(
            title=title,
            description=description,
            category=category,
            venue_id=venue_id,
            duration_minutes=duration_minutes,
            age_restriction=age_restriction,
            poster_url=poster_url
        )
        db.add(event)
        db.commit()
        flash('Мероприятие добавлено!', 'success')
        return redirect(url_for('admin.events'))
    
    categories = ['movie', 'theater', 'concert', 'sport', 'exhibition']
    return render_template('admin/add_event.html', venues=venues, categories=categories)

@bp.route('/events/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        flash('Мероприятие не найдено', 'danger')
        return redirect(url_for('admin.events'))
    
    venues = db.query(Venue).all()
    
    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.category = request.form['category']
        event.venue_id = request.form['venue_id']
        event.duration_minutes = int(request.form['duration_minutes'])
        event.age_restriction = int(request.form['age_restriction'])
        event.poster_url = request.form.get('poster_url')
        db.commit()
        flash('Мероприятие обновлено!', 'success')
        return redirect(url_for('admin.events'))
    
    categories = ['movie', 'theater', 'concert', 'sport', 'exhibition']
    return render_template('admin/edit_event.html', event=event, venues=venues, categories=categories)

@bp.route('/events/delete/<int:event_id>')
@login_required
def delete_event(event_id):
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    event = db.query(Event).get(event_id)
    if event:
        db.delete(event)
        db.commit()
        flash('Мероприятие удалено', 'success')
    else:
        flash('Мероприятие не найдено', 'danger')
    return redirect(url_for('admin.events'))

@bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    all_users = db.query(User).all()
    return render_template('admin/users.html', users=all_users)

@bp.route('/users/toggle/<int:user_id>')
@login_required
def toggle_user(user_id):
    if current_user.role != 'admin':
        return "Доступ запрещён", 403
    db = get_db()
    user = db.query(User).get(user_id)
    if user and user.id != current_user.id:
        user.is_active = not getattr(user, 'is_active', True)
        db.commit()
        status = "разблокирован" if user.is_active else "заблокирован"
        flash(f'Пользователь {user.email} {status}', 'success')
    return redirect(url_for('admin.users'))