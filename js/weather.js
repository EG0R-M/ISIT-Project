let currentWeather = null;
let rainSketch = null;

// Функции для погоды
function getWeatherIcon(type) {
    const icons = { 'rain': '🌧️', 'snow': '❄️', 'clouds': '☁️', 'clear': '☀️' };
    return icons[type] || '☀️';
}

function getWeatherName(type) {
    const names = { 'rain': 'Дождь', 'snow': 'Снег', 'clouds': 'Облачно', 'clear': 'Ясно' };
    return names[type] || 'Ясно';
}

function updateUI(weather) {
    const weatherTypeDiv = document.getElementById('weatherType');
    const temperatureDiv = document.getElementById('temperature');
    const adviceDiv = document.getElementById('adviceText');
    weatherTypeDiv.innerHTML = `${getWeatherIcon(weather.weather_type)} ${getWeatherName(weather.weather_type)}`;
    temperatureDiv.innerHTML = `${weather.temperature}°C`;
    adviceDiv.innerHTML = weather.advice;
}

// Анимации
function showAnimation(type) {
    document.getElementById('rain-container').style.display = 'none';
    document.getElementById('snow-container').style.display = 'none';
    document.getElementById('clouds-container').style.display = 'none';
    document.body.style.background = '#a8cbe8';
    switch(type) {
        case 'rain':
            document.getElementById('rain-container').style.display = 'block';
            startRainAnimation();
            document.body.style.background = '#3a6b9e';
            break;
        case 'snow':
            document.getElementById('snow-container').style.display = 'block';
            startSnowAnimation();
            document.body.style.background = '#7faed4';
            break;
        case 'clouds':
            document.getElementById('clouds-container').style.display = 'block';
            document.body.style.background = '#89b8dd';
            break;
        default:
            document.body.style.background = '#a8cbe8';
    }
}

function startRainAnimation() {
    if (rainSketch) rainSketch.remove();
    const container = document.getElementById('rain-container');
    container.innerHTML = '<div id="rain-canvas-container"></div>';
    rainSketch = new p5((p) => {
        let rain;
        class Particle {
            constructor(x, y, vx, vy) {
                this.pos = p.createVector(x, y);
                this.vel = p.createVector(vx, vy);
                this.acc = p.createVector(0, -0.1);
                this.radius = 2;
            }
            draw() { p.noStroke(); p.fill(200,200,255,180); p.ellipse(this.pos.x, p.height - this.pos.y, this.radius); }
            update() { this.vel.add(this.acc); this.pos.add(this.vel); }
        }
        class RainSplat {
            constructor(drop) {
                this.particles = [];
                for(let i=0;i<6;i++) this.particles.push(new Particle(drop.pos.x,0,p.random(-1.5,1.5),p.random(0,-drop.vel.y/6)));
            }
            draw() { this.particles.forEach(part => part.draw()); }
            update() { this.particles.forEach(part => part.update()); }
            isVisible() { return this.particles.some(part => part.pos.y+part.radius>0); }
        }
        class RainDrop {
            constructor() { this.reset(); this.acc = p.createVector(0,-0.1); this.length=20; this.width=2; }
            draw() { p.noStroke(); p.fill(180,180,255,180); p.rect(this.pos.x, p.height-this.pos.y, this.width, this.length); }
            update() { this.vel.add(this.acc); this.pos.add(this.vel); }
            hasHitFloor() { return this.pos.y-this.length<=0; }
            reset() { this.pos = p.createVector(p.random(p.width), p.random(p.height+100, p.height+1000)); this.vel = p.createVector(0, p.random(-8,-3)); }
        }
        class Rain {
            constructor(n) {
                this.drops = []; for(let i=0;i<n;i++) this.drops.push(new RainDrop());
                this.splats = [];
            }
            draw() { this.drops.forEach(d=>d.draw()); this.splats.forEach(s=>s.draw()); }
            update() { this.drops.forEach(d=>d.update()); this.splats.forEach(s=>s.update()); }
            resolveCollisions() {
                this.drops.forEach(d=>{ if(d.hasHitFloor()) { this.splats.push(new RainSplat(d)); d.reset(); } });
            }
            cullSplats() { this.splats = this.splats.filter(s=>s.isVisible()); }
        }
        p.setup = () => {
            const canvas = p.createCanvas(window.innerWidth, window.innerHeight);
            canvas.parent('rain-canvas-container');
            rain = new Rain(120);
        };
        p.draw = () => {
            p.background(58,107,158,60);
            rain.update();
            rain.resolveCollisions();
            rain.cullSplats();
            rain.draw();
        };
        p.windowResized = () => p.resizeCanvas(window.innerWidth, window.innerHeight);
    }, 'rain-canvas-container');
}

function startSnowAnimation() {
    const canvas = document.getElementById('snow-canvas');
    if(!canvas) return;
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    const ctx = canvas.getContext('2d');
    let particles = [];
    for(let i=0;i<250;i++) {
        particles.push({
            x: Math.random()*canvas.width,
            y: Math.random()*canvas.height,
            r: Math.random()*3+1,
            sy: Math.random()*1.5+0.5,
            sx: Math.random()*0.5-0.25,
            op: Math.random()*0.5+0.3
        });
    }
    function animate() {
        if(!canvas || canvas.style.display==='none') return;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        particles.forEach(p=>{
            p.y += p.sy;
            p.x += p.sx;
            if(p.y > canvas.height) { p.y = -p.r; p.x = Math.random()*canvas.width; }
            if(p.x > canvas.width) p.x = 0;
            if(p.x < 0) p.x = canvas.width;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
            ctx.fillStyle = `rgba(255,255,255,${p.op})`;
            ctx.fill();
        });
        requestAnimationFrame(animate);
    }
    animate();
    window.addEventListener('resize', ()=>{
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

function removeRainCanvas() { if(rainSketch) { rainSketch.remove(); rainSketch=null; } }

// Основной fetch
async function fetchWeather() {
    try {
        const response = await fetch('/weather/api/weather');
        const data = await response.json();
        currentWeather = data;
        updateUI(data);
        showAnimation(data.weather_type);
    } catch(error) {
        console.error('Ошибка погоды:', error);
        document.getElementById('weatherType').innerHTML = '⚠️ Ошибка';
        document.getElementById('temperature').innerHTML = '--°C';
        document.getElementById('adviceText').innerHTML = 'Не удалось загрузить погоду';
    }
}

window.onload = () => { fetchWeather(); };