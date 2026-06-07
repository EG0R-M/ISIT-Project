from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import joinedload
from app.database import get_db
from moduls.ticket import Ticket
from moduls.session import Session
from moduls.event import Event
from moduls.seat import Seat
from moduls.review import Review

bp = Blueprint('profile', __name__)

@bp.route('/')
@login_required
def dashboard():
    return render_template('profile/dashboard.html', user=current_user)

@bp.route('/bookings')
@login_required
def bookings():
    db = get_db()
    tickets = db.query(Ticket).options(
        joinedload(Ticket.session).joinedload(Session.event),
        joinedload(Ticket.seat)
    ).filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('profile/bookings.html', tickets=tickets)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    db = get_db()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        if full_name:
            current_user.full_name = full_name
        if phone is not None:
            current_user.phone = phone
        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Текущий пароль введён неверно.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            if new_password != confirm_password:
                flash('Новый пароль и подтверждение не совпадают.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            if len(new_password) < 6:
                flash('Новый пароль должен содержать не менее 6 символов.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            current_user.password_hash = generate_password_hash(new_password)
            flash('Пароль успешно изменён!', 'success')
        
        db.add(current_user)
        db.commit()
        
        if not (current_password or new_password or confirm_password):
            flash('Профиль обновлён.', 'success')
        
        return redirect(url_for('profile.dashboard'))
    
    return render_template('profile/edit.html', user=current_user)

@bp.route('/reviews')
@login_required
def my_reviews():
    db = get_db()
    reviews = db.query(Review).options(
        joinedload(Review.event)
    ).filter_by(user_id=current_user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile/my_reviews.html', reviews=reviews)

@bp.route('/review/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    db = get_db()
    review = db.query(Review).get(review_id)
    if not review or review.user_id != current_user.id:
        flash('Отзыв не найден.', 'danger')
        return redirect(url_for('profile.my_reviews'))
    db.delete(review)
    db.commit()
    flash('Отзыв удалён.', 'success')
    return redirect(url_for('profile.my_reviews'))

@bp.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    db = get_db()
    review = db.query(Review).get(review_id)
    if not review or review.user_id != current_user.id:
        flash('Отзыв не найден.', 'danger')
        return redirect(url_for('profile.my_reviews'))
    
    if request.method == 'POST':
        review.rating = int(request.form['rating'])
        review.comment = request.form['comment']
        db.commit()
        flash('Отзыв обновлён.', 'success')
        return redirect(url_for('profile.my_reviews'))
    
    return render_template('profile/edit_review.html', review=review)