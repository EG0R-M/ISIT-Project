from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.database import get_db
from moduls.favorite import Favorite
from moduls.event import Event

bp = Blueprint('favorites', __name__, url_prefix='/favorites')

@bp.route('/add/<int:event_id>')
@login_required
def add(event_id):
    db = get_db()
    existing = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first()
    if not existing:
        fav = Favorite(user_id=current_user.id, event_id=event_id)
        db.add(fav)
        db.commit()
        flash('Добавлено в избранное.', 'success')
    else:
        flash('Уже в избранном.', 'info')
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/remove/<int:event_id>')
@login_required
def remove(event_id):
    db = get_db()
    fav = db.query(Favorite).filter_by(user_id=current_user.id, event_id=event_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        flash('Удалено из избранного.', 'success')
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/')
@login_required
def list_favorites():
    db = get_db()
    events = db.query(Event).join(Favorite).filter(Favorite.user_id == current_user.id).all()
    return render_template('profile/favorites.html', events=events)