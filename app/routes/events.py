from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.database import get_db
from app.forms import ReviewForm
from moduls.favorite import Favorite
from moduls.event import Event, EventStatus
from moduls.session import Session
from moduls.ticket import Ticket
from moduls.review import Review
from datetime import datetime
import math

bp = Blueprint('events', __name__)

@bp.route('/')
def list_events():
    db = get_db()
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = db.query(Event)
    
    # Фильтр по статусу: админ видит всё, обычные пользователи – только одобренные
    if not (current_user.is_authenticated and current_user.role == 'admin'):
        query = query.filter(Event.status == EventStatus.APPROVED)
    
    if category:
        query = query.filter_by(category=category)

    total = query.count()
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    if current_user.is_authenticated:
        favorite_ids = {f.event_id for f in db.query(Favorite).filter_by(user_id=current_user.id).all()}
        for event in events:
            event.is_favorited = event.id in favorite_ids
    else:
        for event in events:
            event.is_favorited = False

    total_pages = math.ceil(total / per_page) if total > 0 else 1
    has_prev = page > 1
    has_next = page < total_pages

    categories = [
        ('movie', 'Кино'),
        ('theater', 'Театр'),
        ('concert', 'Концерт'),
        ('sport', 'Спорт'),
        ('exhibition', 'Выставка')
    ]

    pagination = {
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': page - 1 if has_prev else None,
        'next_num': page + 1 if has_next else None,
        'pages': total_pages,
        'page': page,
        'total': total
    }

    def iter_pages():
        for i in range(1, total_pages + 1):
            yield i
    pagination['iter_pages'] = iter_pages

    return render_template('events/list.html',
                          events=events,
                          categories=categories,
                          selected=category,
                          pagination=pagination,
                          page=page)

@bp.route('/<int:event_id>')
def detail(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return "Событие не найдено", 404

    # Если пользователь не админ и событие не одобрено – запрещаем просмотр
    if not (current_user.is_authenticated and current_user.role == 'admin'):
        if event.status != EventStatus.APPROVED:
            flash('Мероприятие находится на модерации или отклонено.', 'warning')
            return redirect(url_for('events.list_events'))

    sessions = db.query(Session).filter_by(event_id=event_id, is_cancelled=False).order_by(Session.start_time).all()
    reviews = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).limit(10).all()

    user_can_review = False
    is_favorited = False
    if current_user.is_authenticated:
        now = datetime.now()
        user_can_review = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.status == 'paid',
            Ticket.session.has(Session.start_time < now)
        ).first() is not None
        is_favorited = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first() is not None

    return render_template('events/detail.html',
                          event=event,
                          sessions=sessions,
                          reviews=reviews,
                          user_can_review=user_can_review,
                          is_favorited=is_favorited)

@bp.route('/search')
def search():
    db = get_db()
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = db.query(Event)
    if not (current_user.is_authenticated and current_user.role == 'admin'):
        query = query.filter(Event.status == EventStatus.APPROVED)
    if q:
        query = query.filter(Event.title.contains(q) | Event.description.contains(q))
    if category:
        query = query.filter_by(category=category)
    if date_from:
        subq_from = db.query(Session.event_id).filter(Session.start_time >= date_from).subquery()
        query = query.filter(Event.id.in_(subq_from))
    if date_to:
        subq_to = db.query(Session.event_id).filter(Session.start_time <= date_to).subquery()
        query = query.filter(Event.id.in_(subq_to))

    total = query.count()
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    if current_user.is_authenticated:
        favorite_ids = {f.event_id for f in db.query(Favorite).filter_by(user_id=current_user.id).all()}
        for event in events:
            event.is_favorited = event.id in favorite_ids
    else:
        for event in events:
            event.is_favorited = False

    total_pages = math.ceil(total / per_page) if total > 0 else 1
    has_prev = page > 1
    has_next = page < total_pages

    categories = [
        ('movie', 'Кино'),
        ('theater', 'Театр'),
        ('concert', 'Концерт'),
        ('sport', 'Спорт'),
        ('exhibition', 'Выставка')
    ]

    pagination = {
        'has_prev': has_prev,
        'has_next': has_next,
        'prev_num': page - 1 if has_prev else None,
        'next_num': page + 1 if has_next else None,
        'pages': total_pages,
        'page': page,
        'total': total,
        'iter_pages': lambda: range(1, total_pages + 1)
    }

    return render_template('events/search.html',
                          events=events,
                          categories=categories,
                          q=q,
                          selected=category,
                          date_from=date_from,
                          date_to=date_to,
                          pagination=pagination,
                          page=page)

@bp.route('/<int:event_id>/reviews', methods=['GET', 'POST'])
def reviews(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return "Событие не найдено", 404

    if not (current_user.is_authenticated and current_user.role == 'admin'):
        if event.status != EventStatus.APPROVED:
            flash('Мероприятие недоступно.', 'warning')
            return redirect(url_for('events.list_events'))

    form = ReviewForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        has_ticket = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.status == 'paid'
        ).first() is not None

        now = datetime.now()
        has_passed = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.session.has(Session.start_time < now),
            Ticket.status == 'paid'
        ).first() is not None

        if not has_ticket:
            flash('Вы можете оставить отзыв только после покупки билета.', 'warning')
            return redirect(url_for('events.reviews', event_id=event_id))

        if not has_passed:
            flash('Вы можете оставить отзыв только после того, как мероприятие прошло.', 'warning')
            return redirect(url_for('events.reviews', event_id=event_id))

        existing = db.query(Review).filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing:
            flash('Вы уже оставили отзыв на это событие.', 'warning')
        else:
            review = Review(user_id=current_user.id, event_id=event_id,
                            rating=form.rating.data, comment=form.comment.data, is_verified=True)
            db.add(review)
            db.commit()
            flash('Спасибо за отзыв!', 'success')
        return redirect(url_for('events.reviews', event_id=event_id))

    reviews_list = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).all()
    return render_template('events/reviews.html', form=form, event=event, reviews=reviews_list)