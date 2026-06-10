from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.database import get_db
from moduls.user import User

class RegistrationForm(FlaskForm):
    role = RadioField('Вы собираетесь', choices=[
        ('user', 'Покупать билеты'),
        ('organizer', 'Организовывать мероприятия')
    ], default='user')
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Полное имя', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=20)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        db = get_db()
        user = db.query(User).filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже занят.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')