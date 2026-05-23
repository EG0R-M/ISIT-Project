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