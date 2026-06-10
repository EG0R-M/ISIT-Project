from flask import Blueprint, jsonify
from app.database import get_db
from moduls.venue import Venue
from moduls.event import Event
from moduls.session import Session
from moduls.ticket import Ticket
from moduls.review import Review
from sqlalchemy import func
from datetime import datetime, timedelta

api_venues_bp = Blueprint('api_venues', 'name', url_prefix='/api/venues')

def slugify_venue_name(name):
    """Преобразует название заведения в имя файла"""
    return name.replace(' ', '_').replace("'", '').replace('«', '').replace('»', '')

@api_venues_bp.route('/popular', methods=['GET'])
def get_popular_venues():
    db = get_db()
    one_year_ago = datetime.now() - timedelta(days=365)
    
    # Проверяем, есть ли оплаченные билеты за последний год
    has_paid_tickets = db.query(Ticket).filter(
        Ticket.status == 'paid',
        Ticket.paid_at >= one_year_ago
    ).first() is not None
    
    # Если оплаченных билетов нет — просто показываем все заведения (или первые 10)
    if not has_paid_tickets:
        venues = db.query(Venue).limit(10).all()
        result = []
        for venue in venues:
            result.append({
                'id': venue.id,
                'name': venue.name,
                'city': venue.city,
                'rating': 50,  # базовый рейтинг для отображения
                'image_url': venue.image_url or '/static/images/venues/default.jpg'
            })
        return jsonify(result)
    
    # Если оплаченные билеты есть — считаем рейтинг как раньше
    max_sales = db.query(func.sum(Ticket.price_paid)).join(
        Session, Ticket.session_id == Session.id
    ).join(
        Event, Session.event_id == Event.id
    ).filter(
        Ticket.status == 'paid',
        Ticket.paid_at >= one_year_ago
    ).scalar() or 1

    venues = db.query(Venue).all()
    result = []
    for venue in venues:
        sales = db.query(func.sum(Ticket.price_paid)).join(
            Session, Ticket.session_id == Session.id
        ).join(
            Event, Session.event_id == Event.id
        ).filter(
            Event.venue_id == venue.id,
            Ticket.status == 'paid',
            Ticket.paid_at >= one_year_ago
        ).scalar() or 0

        avg_rating = db.query(func.avg(Review.rating)).join(
            Event, Review.event_id == Event.id
        ).filter(
            Event.venue_id == venue.id,
            Review.created_at >= one_year_ago
        ).scalar() or 0

        sales_score_float = float(sales_score) if sales_score else 0
        rating_score_float = float(rating_score) if rating_score else 0
        rating = (sales_score_float * 0.6 + rating_score_float * 0.4) * 100
        rating = round(rating, 2)

        # Включаем все заведения с ненулевым рейтингом или хотя бы с событием
        if rating > 0 or sales > 0 or avg_rating > 0:
            result.append({
            'id': venue.id,
            'name': venue.name,
            'city': venue.city,
            'rating': rating,
            'image_url': venue.image_url or '/static/images/venues/default.jpg'
        })

    result.sort(key=lambda x: x['rating'], reverse=True)
    return jsonify(result[:10])
