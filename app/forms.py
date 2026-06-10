from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, NumberRange
from app.database import get_db
from moduls.user import User

class RegistrationForm(FlaskForm):
    role = RadioField('Вы собираетесь', choices=[
        ('user', '🎫 Покупать билеты'),
        ('organizer', '🎪 Организовывать мероприятия')
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


class AdminEventForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(min=2, max=255)])
    description = TextAreaField('Описание', validators=[Optional()])
    category = SelectField('Категория', choices=[
        ('movie', 'Кино'), ('theater', 'Театр'), ('concert', 'Концерт'),
        ('sport', 'Спорт'), ('exhibition', 'Выставка')
    ], validators=[DataRequired()])
    venue_id = SelectField('Площадка', coerce=int, validators=[DataRequired()])
    duration_minutes = IntegerField('Длительность (минуты)', validators=[Optional()], default=90)
    age_restriction = SelectField('Возрастное ограничение', coerce=int, choices=[
        (0, '0+'), (6, '6+'), (12, '12+'), (16, '16+'), (18, '18+')
    ], default=0)
    poster_url = StringField('URL постера', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Сохранить')


class ProfileForm(FlaskForm):
    full_name = StringField('Полное имя', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Телефон', validators=[Optional(), Length(max=20)])
    current_password = PasswordField('Текущий пароль', validators=[Optional()])
    new_password = PasswordField('Новый пароль', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Подтверждение пароля', validators=[Optional(), EqualTo('new_password')])
    submit = SubmitField('Сохранить изменения')


class ReviewForm(FlaskForm):
    rating = SelectField('Оценка', coerce=int, choices=[
        (5, '5 — Отлично'), (4, '4 — Хорошо'), (3, '3 — Средне'),
        (2, '2 — Плохо'), (1, '1 — Ужасно')
    ], default=5, validators=[DataRequired()])
    comment = TextAreaField('Комментарий', validators=[Optional(), Length(max=2000)])
    submit = SubmitField('Отправить отзыв')