from flask import Blueprint, render_template, jsonify, current_app
import requests
import random

bp = Blueprint('weather', __name__, url_prefix='/weather')

WEATHER_ADVICES = {
    'rain': [
        "Не забудьте зонт! Дождь может усилиться.",
        "Одевайтесь теплее и берите непромокаемую куртку.",
        "Будьте осторожны за рулём - дороги скользкие.",
        "Отличный день, чтобы остаться дома с чаем!",
        "Наденьте резиновые сапоги - лужи неизбежны!"
    ],
    'snow': [
        "Наденьте шапку и варежки! Мороз щиплет щёки.",
        "Осторожно на дорогах - гололёд!",
        "Отличная погода для лепки снеговика!",
        "Не забудьте шарф - защитите шею.",
        "Самое время для катания на лыжах!"
    ],
    'clouds': [
        "Пасмурно, но зонт можете не брать.",
        "Возьмите ветровку - ветер может быть прохладным.",
        "Хороший день для чтения книги у окна.",
        "Погода подходит для спокойной прогулки.",
        "Отличный день для просмотра кино дома!"
    ],
    'clear': [
        "Отличная погода для прогулки! Не забудьте очки.",
        "Нанесите солнцезащитный крем - солнце активное!",
        "Пейте больше воды, чтобы избежать обезвоживания.",
        "Самое время для велопрогулки или пикника!",
        "Наденьте головной убор, чтобы не перегреться."
    ]
}

def get_random_advice(weather_type):
    advices = WEATHER_ADVICES.get(weather_type, WEATHER_ADVICES['clear'])
    return random.choice(advices)

def get_weather_data():
    api_key = current_app.config.get('OPENWEATHER_API_KEY', '')
    city = current_app.config.get('WEATHER_CITY', 'Moscow')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code == 200:
            weather_main = data['weather'][0]['main'].lower()
            temp = round(data['main']['temp'])
            if 'rain' in weather_main or 'drizzle' in weather_main:
                wtype = 'rain'
            elif 'snow' in weather_main:
                wtype = 'snow'
            elif 'cloud' in weather_main or 'overcast' in weather_main:
                wtype = 'clouds'
            elif 'clear' in weather_main:
                wtype = 'clear'
            else:
                wtype = 'clear'
            return {
                'weather_type': wtype,
                'temperature': temp,
                'advice': get_random_advice(wtype),
                'city': city,
                'description': data['weather'][0]['description']
            }
    except Exception as e:
        current_app.logger.error(f"Weather API error: {e}")
    # fallback
    return {
        'weather_type': 'clear',
        'temperature': 10,
        'advice': get_random_advice('clear'),
        'city': city,
        'description': 'неизвестно'
    }

@bp.route('/')
def weather_page():
    # Полная страница погоды с анимациями (если нужно)
    return render_template('weather/weather_index.html')

@bp.route('/api/weather')
def api_weather():
    return jsonify(get_weather_data())