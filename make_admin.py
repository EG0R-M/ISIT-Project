from app import create_app
from app.database import get_db
from moduls.user import User
app = create_app()
with app.app_context():
    db = get_db()
    user = db.query(User).filter_by(email='daniilaroslav162@gmail.com').first()
    if user:
        user.role = 'admin'
        db.commit()
        print(f'User {user.email} is now admin')
    else:
        print('User not found')