from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from app.database import close_db

# Глобальная переменная для login_manager (чтобы избежать цикличных импортов)
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Инициализация LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа.'

    # Регистрация teardown для закрытия сессии
    app.teardown_appcontext(close_db)

    # Импорт моделей и функции user_loader (после инициализации app)
    from moduls.user import User
    from app.database import get_db

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        return db.query(User).get(int(user_id))

    # Регистрация blueprints
    from app.routes import auth, events, bookings, profile, admin
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(events.bp, url_prefix='/events')
    app.register_blueprint(bookings.bp, url_prefix='/bookings')
    app.register_blueprint(profile.bp, url_prefix='/profile')
    app.register_blueprint(admin.bp, url_prefix='/admin')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app