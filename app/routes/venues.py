from flask import Blueprint, render_template, abort
from app.database import get_db
from moduls.venue import Venue
from moduls.event import Event
from moduls.session import Session
from datetime import datetime

bp = Blueprint('venues', __name__, url_prefix='/venues')

@bp.route('/')
def list_venues():
    db = get_db()
    venues = db.query(Venue).order_by(Venue.name).all()
    return render_template('venues/list.html', venues=venues)

@bp.route('/<int:venue_id>')
def detail(venue_id):
    db = get_db()
    venue = db.query(Venue).get(venue_id)
    if not venue:
        abort(404)
    
    # Находим все события этого заведения, сортируем по дате ближайшего сеанса
    events = db.query(Event).filter_by(venue_id=venue_id).all()
    # Для каждого события подгрузим ближайший будущий сеанс
    now = datetime.now()
    for event in events:
        next_session = db.query(Session).filter(
            Session.event_id == event.id,
            Session.start_time > now,
            Session.is_cancelled == False
        ).order_by(Session.start_time).first()
        event.next_session = next_session
    
    return render_template('venues/detail.html', venue=venue, events=events)