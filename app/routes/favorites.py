from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import login_required, current_user
from app.database import get_db
from moduls.favorite import Favorite
from moduls.event import Event
import math

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
    referer = request.referrer
    if referer:
        return redirect(referer)
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
    else:
        flash('Не найдено в избранном.', 'warning')
    referer = request.referrer
    if referer:
        return redirect(referer)
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/')
@login_required
def list_favorites():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    query = db.query(Event).join(Favorite, Favorite.event_id == Event.id).filter(Favorite.user_id == current_user.id).order_by(Favorite.id.desc())
    total = query.count()
    offset = (page - 1) * per_page
    events = query.offset(offset).limit(per_page).all()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    has_prev = page > 1
    has_next = page < total_pages
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
    return render_template('profile/favorites.html', events=events, pagination=pagination, page=page)