import os
from dotenv import load_dotenv

# Загружаем .env из корня проекта (явно указываем путь)
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///booking.db')
    
    OPENWEATHER_API_KEY = 'your-openweather-api-key-here'
    WEATHER_CITY = os.environ.get('WEATHER_CITY', 'Irkutsk')