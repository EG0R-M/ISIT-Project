from flask import Blueprint, render_template, jsonify, current_app
import requests
import random

bp = Blueprint('weather', __name__, url_prefix='/weather')

WEATHER_ADVICES = {
    'rain': ["Не забудьте зонт!", "Одевайтесь теплее", "Будьте осторожны на дорогах"],
    'snow': ["Наденьте шапку и варежки!", "Осторожно, гололёд!", "Отличная погода для снежков"],
    'clouds': ["Пасмурно, но зонт не нужен", "Возьмите ветровку", "Хороший день для чтения"],
    'clear': ["Отличная погода для прогулки!", "Нанесите солнцезащитный крем", "Пейте больше воды"]
}

def get_advice(weather_type):
    return random.choice(WEATHER_ADVICES.get(weather_type, WEATHER_ADVICES['clear']))

def get_weather():
    api_key = current_app.config.get('OPENWEATHER_API_KEY', '')
    city = current_app.config.get('WEATHER_CITY', 'Irkutsk')
    
    # Отладочный вывод (в консоль Flask, безопасно)
    print(f"DEBUG: api_key = {api_key[:10] if api_key else 'None'}...")
    
    if not api_key:
        current_app.logger.warning("OPENWEATHER_API_KEY не задан")
        return {
            'weather_type': 'clear',
            'temperature': 10,
            'advice': 'Ключ API не настроен. Проверьте .env',
            'city': city,
            'description': 'ошибка конфигурации'
        }

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if response.status_code == 200:
            w = data['weather'][0]['main'].lower()
            if 'rain' in w: wtype = 'rain'
            elif 'snow' in w: wtype = 'snow'
            elif 'cloud' in w: wtype = 'clouds'
            else: wtype = 'clear'
            return {
                'weather_type': wtype,
                'temperature': round(data['main']['temp']),
                'advice': get_advice(wtype),
                'city': city,
                'description': data['weather'][0]['description']
            }
        else:
            current_app.logger.error(f"Weather API error {response.status_code}: {data.get('message', '')}")
    except Exception as e:
        current_app.logger.error(f"Weather request failed: {e}")

    return {
        'weather_type': 'clear',
        'temperature': 10,
        'advice': 'Ошибка загрузки погоды',
        'city': city,
        'description': 'сервис временно недоступен'
    }

@bp.route('/')
def weather_page():
    return render_template('weather/weather_index.html')

@bp.route('/api/weather')
def api_weather():
    return jsonify(get_weather())