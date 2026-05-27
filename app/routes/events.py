from flask import Blueprint, render_template, request
from app.database import get_db
from moduls.event import Event
from moduls.session import Session
from sqlalchemy import func

bp = Blueprint('events', __name__)

@bp.route('/')
def list_events():
    db = get_db()
    category = request.args.get('category')
    query = db.query(Event)
    if category:
        query = query.filter_by(category=category)
    events = query.all()
    categories = ['movie', 'theater', 'concert', 'sport', 'exhibition']
    return render_template('events/list.html', events=events, categories=categories, selected=category)

@bp.route('/<int:event_id>')
def detail(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return "Событие не найдено", 404
    # Получаем сеансы этого события
    sessions = db.query(Session).filter_by(event_id=event_id, is_cancelled=False).order_by(Session.start_time).all()
    return render_template('events/detail.html', event=event, sessions=sessions)

@bp.route('/<int:event_id>/reviews', methods=['GET', 'POST'])
def reviews(event_id):
    db = get_db()
    event = db.query(Event).get(event_id)
    if not event:
        return "Событие не найдено", 404
    if request.method == 'POST' and current_user.is_authenticated:
        rating = int(request.form['rating'])
        comment = request.form['comment']
        from moduls.review import Review
        existing = db.query(Review).filter_by(user_id=current_user.id, event_id=event_id).first()
        if existing:
            flash('Вы уже оставили отзыв на это событие.', 'warning')
        else:
            review = Review(user_id=current_user.id, event_id=event_id, rating=rating, comment=comment, is_verified=False)
            db.add(review)
            db.commit()
            flash('Спасибо за отзыв!', 'success')
        return redirect(url_for('events.reviews', event_id=event_id))
    reviews_list = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).all()
    return render_template('events/reviews.html', event=event, reviews=reviews_list)

@bp.route('/search')
def search():
    db = get_db()
    q = request.args.get('q', '')
    category = request.args.get('category', '')
    date_from = request.args.get('date_from', '')
    query = db.query(Event)
    if q:
        query = query.filter(Event.title.contains(q) | Event.description.contains(q))
    if category:
        query = query.filter_by(category=category)
    if date_from:
        # простой фильтр: ищем события, у которых есть сеансы после указанной даты
        from moduls.session import Session
        subq = db.query(Session.event_id).filter(Session.start_time >= date_from).subquery()
        query = query.filter(Event.id.in_(subq))
    events = query.all()
    categories = ['movie', 'theater', 'concert', 'sport', 'exhibition']
    return render_template('events/search.html', events=events, categories=categories, q=q, selected=category, date_from=date_from)