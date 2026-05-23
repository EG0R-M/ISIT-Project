from flask import g
from moduls import init_db

def get_db():
    """Возвращает сессию SQLAlchemy для текущего запроса"""
    if 'db' not in g:
        # Используем строку подключения из конфига Flask
        from flask import current_app
        db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
        SessionLocal, _ = init_db(db_url)
        g.db = SessionLocal()
    return g.db

def close_db(e=None):
    """Закрывает сессию после запроса"""
    db = g.pop('db', None)
    if db is not None:
        db.close()