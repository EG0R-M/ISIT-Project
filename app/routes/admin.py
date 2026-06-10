from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from app.database import get_db
from app.forms import AdminEventForm
from moduls.user import User
from moduls.event import Event, EventStatus
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
    form = AdminEventForm()
    form.venue_id.choices = [(v.id, f'{v.name} ({v.city})') for v in db.query(Venue).all()]

    if form.validate_on_submit():
        event = Event(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            venue_id=form.venue_id.data,
            duration_minutes=form.duration_minutes.data,
            age_restriction=form.age_restriction.data,
            poster_url=form.poster_url.data
        )
        db.add(event)
        db.commit()
        flash('Мероприятие добавлено!', 'success')
        return redirect(url_for('admin.events'))

    return render_template('admin/add_event.html', form=form)

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

    form = AdminEventForm(obj=event)
    form.venue_id.choices = [(v.id, f'{v.name} ({v.city})') for v in db.query(Venue).all()]

    if form.validate_on_submit():
        form.populate_obj(event)
        db.commit()
        flash('Мероприятие обновлено!', 'success')
        return redirect(url_for('admin.events'))

    return render_template('admin/edit_event.html', form=form, event=event)

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

@bp.route('/events/pending')
@login_required
def pending_events():
    if current_user.role != 'admin':
        abort(403)
    db = get_db()
    # Используйте сравнение с объектом Enum, а не строкой
    pending = db.query(Event).filter(Event.status == EventStatus.PENDING).order_by(Event.created_at).all()
    return render_template('admin/pending_events.html', events=pending)

@bp.route('/events/pending/<int:event_id>')
@login_required
def view_pending_event(event_id):
    if current_user.role != 'admin':
        abort(403)
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event or event.status != EventStatus.PENDING:
        flash('Мероприятие не найдено или уже обработано.', 'warning')
        return redirect(url_for('admin.pending_events'))
    return render_template('admin/event_review.html', event=event)

@bp.route('/events/approve/<int:event_id>')
@login_required
def approve_event(event_id):
    if current_user.role != 'admin':
        abort(403)
    db = get_db()
    event = db.query(Event).get(event_id)
    if event:
        event.status = EventStatus.APPROVED   # не 'approved'
        db.commit()
        flash(f'Мероприятие "{event.title}" одобрено', 'success')
    else:
        flash('Мероприятие не найдено', 'danger')
    return redirect(url_for('admin.pending_events'))

@bp.route('/events/reject/<int:event_id>')
@login_required
def reject_event(event_id):
    if current_user.role != 'admin':
        abort(403)
    db = get_db()
    event = db.query(Event).get(event_id)
    if event:
        event.status = EventStatus.REJECTED   # не 'rejected'
        db.commit()
        flash(f'Мероприятие "{event.title}" отклонено', 'warning')
    else:
        flash('Мероприятие не найдено', 'danger')
    return redirect(url_for('admin.pending_events'))