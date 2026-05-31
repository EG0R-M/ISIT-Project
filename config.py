import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-12345'
 
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///booking.db'
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
    WEATHER_CITY = 'Irkutsk'
