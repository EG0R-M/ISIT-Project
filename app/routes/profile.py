from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from moduls.ticket import Ticket
from moduls.session import Session
from moduls.event import Event
from moduls.seat import Seat

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
    for t in tickets:
        t.session = db.query(Session).get(t.session_id)
        if t.session:
            t.event = db.query(Event).get(t.session.event_id)
        t.seat = db.query(Seat).get(t.seat_id)
    return render_template('profile/bookings.html', tickets=tickets)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    db = get_db()
    
    if request.method == 'POST':
        # Обновляем основные данные
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        if full_name:
            current_user.full_name = full_name
        if phone is not None:  # позволяет сохранить пустую строку
            current_user.phone = phone
        
        # Проверка смены пароля
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            # Проверяем текущий пароль
            if not check_password_hash(current_user.password_hash, current_password):
                flash('Текущий пароль введён неверно.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            # Проверяем, что новый пароль совпадает с подтверждением
            if new_password != confirm_password:
                flash('Новый пароль и подтверждение не совпадают.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            # Проверяем минимальную длину пароля
            if len(new_password) < 6:
                flash('Новый пароль должен содержать не менее 6 символов.', 'danger')
                return render_template('profile/edit.html', user=current_user)
            
            # Обновляем пароль
            current_user.password_hash = generate_password_hash(new_password)
            flash('Пароль успешно изменён!', 'success')
        
        db.add(current_user)
        db.commit()
        
        if not (current_password or new_password or confirm_password):
            flash('Профиль обновлён.', 'success')
        
        return redirect(url_for('profile.dashboard'))
    
    return render_template('profile/edit.html', user=current_user)