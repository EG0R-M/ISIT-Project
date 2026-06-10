import os
from dotenv import load_dotenv
from pathlib import Path

# Принудительно загружаем .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///booking.db')
    
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
    WEATHER_CITY = os.environ.get('WEATHER_CITY', 'Irkutsk')
    
    YANDEX_MAPS_API_KEY = os.environ.get('YANDEX_MAPS_API_KEY', '')
    
    # Отладка
    print(f"DEBUG: YANDEX_MAPS_API_KEY from env = {YANDEX_MAPS_API_KEY}")