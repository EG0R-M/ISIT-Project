from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.database import get_db
from moduls.event import Event
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
    if category:
        query = query.filter_by(category=category)
    
    total = query.count()
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    
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
        'per_page': per_page,
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
    
    sessions = db.query(Session).filter_by(event_id=event_id, is_cancelled=False).order_by(Session.start_time).all()
    
    # Получаем отзывы для этого события (последние 10)
    reviews = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).limit(10).all()
    
    # Проверяем, может ли текущий пользователь оставить отзыв
    user_can_review = False
    if current_user.is_authenticated:
        now = datetime.now()
        user_can_review = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.status == 'paid',
            Ticket.session.has(Session.start_time < now)
        ).first() is not None
    
    return render_template('events/detail.html', 
                          event=event, 
                          sessions=sessions,
                          reviews=reviews,
                          user_can_review=user_can_review)

@bp.route('/search')
def search():
    db = get_db()
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    query = db.query(Event)
    if q:
        query = query.filter(Event.title.contains(q) | Event.description.contains(q))
    if category:
        query = query.filter_by(category=category)
    if date_from:
        subq = db.query(Session.event_id).filter(Session.start_time >= date_from).subquery()
        query = query.filter(Event.id.in_(subq))
    
    total = query.count()
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    
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
    
    return render_template('events/search.html', 
                          events=events, 
                          categories=categories, 
                          q=q, 
                          selected=category, 
                          date_from=date_from,
                          pagination=pagination,
                          page=page)

@bp.route('/<int:event_id>/reviews', methods=['GET', 'POST'])
def reviews(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return "Событие не найдено", 404
    
    if request.method == 'POST' and current_user.is_authenticated:
        has_ticket = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.status == 'paid'
        ).first() is not None
        
        current_time = datetime.now()
        has_passed = db.query(Ticket).filter(
            Ticket.user_id == current_user.id,
            Ticket.session.has(event_id=event_id),
            Ticket.session.has(Session.start_time < current_time),
            Ticket.status == 'paid'
        ).first() is not None
        
        if not has_ticket:
            flash('Вы можете оставить отзыв только после покупки билета.', 'warning')
            return redirect(url_for('events.reviews', event_id=event_id))
        
        if not has_passed:
            flash('Вы можете оставить отзыв только после того, как мероприятие прошло.', 'warning')
            return redirect(url_for('events.reviews', event_id=event_id))
        
        rating = int(request.form['rating'])
        comment = request.form['comment']
        
        existing = db.query(Review).filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing:
            flash('Вы уже оставили отзыв на это событие.', 'warning')
        else:
            review = Review(user_id=current_user.id, event_id=event_id, rating=rating, comment=comment, is_verified=True)
            db.add(review)
            db.commit()
            flash('Спасибо за отзыв!', 'success')
        return redirect(url_for('events.reviews', event_id=event_id))
    
    reviews_list = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).all()
    return render_template('events/reviews.html', event=event, reviews=reviews_list)