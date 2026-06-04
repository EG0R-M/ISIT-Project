from flask import Flask, render_template, jsonify
import requests
import random
import os
app = Flask(__name__)


# Вставьте свой API ключ OpenWeatherMap
API_KEY = '9bddc2147fbae8b78bbc7e57e19a0852'
CITY = "Irkutsk"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ru"

# Списки советов для каждого типа погоды
WEATHER_ADVICES = {
    'rain': [
        "Не забудьте зонт! Дождь может усилиться в любой момент.",
        "Одевайтесь теплее и берите непромокаемую куртку.",
        "Будьте осторожны за рулём - дороги скользкие от дождя.",
        "Отличный день, чтобы остаться дома с чашкой горячего чая!",
        "Наденьте резиновые сапоги - лужи неизбежны!"
    ],
    'snow': [
        "Наденьте шапку и варежки! Мороз щиплет щёки.",
        "Осторожно на дорогах - гололёд! Делайте маленькие шаги.",
        "Отличная погода для лепки снеговика и игры в снежки!",
        "Не забудьте шарф - защитите шею от холодного ветра.",
        "Самое время для катания на лыжах или сноуборде!"
    ],
    'clouds': [
        "Пасмурно, но зонт можете не брать - дождя не ожидается.",
        "Возьмите ветровку - ветер может быть прохладным.",
        "Хороший день для чтения книги у окна с чашечкой кофе.",
        "Погода подходит для спокойной прогулки в парке.",
        "Отличный день для просмотра кино дома!"
    ],
    'clear': [
        "Отличная погода для прогулки! Не забудьте солнцезащитные очки.",
        "Нанесите солнцезащитный крем - солнце активное!",
        "Пейте больше воды, чтобы избежать обезвоживания.",
        "Самое время для велопрогулки или пикника!",
        "Наденьте головной убор, чтобы не перегреться."
    ]
}

def get_random_advice(weather_type):
    """Возвращает случайный совет для данного типа погоды"""
    advices = WEATHER_ADVICES.get(weather_type, WEATHER_ADVICES['clear'])
    return random.choice(advices)

def get_weather():
    """Получение данных о погоде с API"""
    try:
        response = requests.get(URL)
        data = response.json()
        
        if response.status_code == 200:
            weather_main = data['weather'][0]['main'].lower()
            temperature = round(data['main']['temp'])
            
            # Преобразуем тип погоды
            if 'rain' in weather_main or 'drizzle' in weather_main:
                weather_type = 'rain'
            elif 'snow' in weather_main:
                weather_type = 'snow'
            elif 'cloud' in weather_main or 'overcast' in weather_main:
                weather_type = 'clouds'
            elif 'clear' in weather_main:
                weather_type = 'clear'
            else:
                weather_type = 'clear'
            
            return {
                'weather_type': weather_type,
                'temperature': temperature,
                'advice': get_random_advice(weather_type),
                'city': CITY,
                'description': data['weather'][0]['description']
            }
        else:
            return get_fallback_weather()
    except Exception as e:
        print(f"Ошибка API: {e}")
        return get_fallback_weather()

def get_fallback_weather():
    """Запасной вариант, если API не работает"""
    return {
        'weather_type': 'clear',
        'temperature': 10,
        'advice': get_random_advice('clear'),
        'city': CITY,
    }

@app.route('/')
def index():
    return render_template('weather_index.html')

@app.route('/api/weather')
def api_weather():
    return jsonify(get_weather())

if __name__ == '__main__':
    app.run(debug=True)