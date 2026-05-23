from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.database import get_db
from moduls.user import User
from moduls.event import Event
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