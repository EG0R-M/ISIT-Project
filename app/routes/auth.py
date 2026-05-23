from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_db
from moduls.user import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        phone = request.form['phone']
        password = request.form['password']
        confirm = request.form['confirm_password']
        
        if password != confirm:
            flash('Пароли не совпадают.', 'danger')
            return render_template('auth/register.html')
        
        db = get_db()
        existing = db.query(User).filter_by(email=email).first()
        if existing:
            flash('Email уже зарегистрирован.', 'danger')
            return render_template('auth/register.html')
        
        hashed = generate_password_hash(password)
        new_user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            password_hash=hashed,
            role='user'
        )
        db.add(new_user)
        db.commit()
        flash('Регистрация успешна! Теперь войдите.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        user = db.query(User).filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'danger')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('index'))