from flask import Flask, render_template
from flask_login import LoginManager
from config import Config
from app.database import close_db
from app.extensions import csrf

login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите для доступа.'

    csrf.init_app(app)

    app.teardown_appcontext(close_db)

    from moduls.user import User
    from app.database import get_db

    @login_manager.user_loader
    def load_user(user_id):
        db = get_db()
        return db.query(User).get(int(user_id))

    # Jinja2 custom filters
    @app.template_filter('datetime')
    def format_datetime(value, fmt='%d.%m.%Y %H:%M'):
        if value is None:
            return ''
        return value.strftime(fmt)

    @app.template_filter('number')
    def format_number(value):
        if value is None:
            return ''
        return f'{value:,.2f}'.replace(',', ' ')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    # Регистрация всех blueprint'ов
    from app.routes import auth, events, bookings, profile, admin, favorites, api, venues
    from app.routes.api_venues import api_venues_bp
    from app.routes.weather import bp as weather_bp
    from app.routes.user_events import bp as user_events_bp
    
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(events.bp, url_prefix='/events')
    app.register_blueprint(bookings.bp, url_prefix='/bookings')
    app.register_blueprint(profile.bp, url_prefix='/profile')
    app.register_blueprint(admin.bp, url_prefix='/admin')
    app.register_blueprint(favorites.bp)
    app.register_blueprint(api.bp)
    app.register_blueprint(venues.bp)
    app.register_blueprint(weather_bp)          # <-- погода
    app.register_blueprint(api_venues_bp)
    app.register_blueprint(user_events_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app