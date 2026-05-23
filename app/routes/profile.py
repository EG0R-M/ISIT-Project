from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.database import get_db
from moduls.ticket import Ticket
from moduls.session import Session
from moduls.event import Event

bp = Blueprint('profile', __name__)

@bp.route('/')
@login_required
def dashboard():
    return render_template('profile/dashboard.html', user=current_user)

@bp.route('/bookings')
@login_required
def bookings():
    db = get_db()
    tickets = db.query(Ticket).filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    # Подгрузим сеансы и события для отображения
    for t in tickets:
        t.session = db.query(Session).get(t.session_id)
        if t.session:
            t.event = db.query(Event).get(t.session.event_id)
    return render_template('profile/bookings.html', tickets=tickets)