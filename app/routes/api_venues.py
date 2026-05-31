from flask import Blueprint, jsonify
from app.database import get_db
from moduls.venue import Venue
from moduls.event import Event
from moduls.session import Session
from moduls.ticket import Ticket
from moduls.review import Review
from sqlalchemy import func
from datetime import datetime, timedelta

api_venues_bp = Blueprint('api_venues', __name__, url_prefix='/api/venues')

@api_venues_bp.route('/popular', methods=['GET'])
def get_popular_venues():
    db = get_db()
    one_year_ago = datetime.now() - timedelta(days=365)
    venues = db.query(Venue).all()

    # Максимальные продажи для нормировки (преобразуем в float)
    max_sales = db.query(func.sum(Ticket.price_paid)).join(
        Session, Ticket.session_id == Session.id
    ).join(
        Event, Session.event_id == Event.id
    ).filter(
        Ticket.status == 'paid',
        Ticket.paid_at >= one_year_ago
    ).scalar()
    if max_sales is None:
        max_sales = 1
    else:
        max_sales = float(max_sales)

    result = []
    for venue in venues:
        # Сумма продаж за год (преобразуем в float)
        sales = db.query(func.sum(Ticket.price_paid)).join(
            Session, Ticket.session_id == Session.id
        ).join(
            Event, Session.event_id == Event.id
        ).filter(
            Event.venue_id == venue.id,
            Ticket.status == 'paid',
            Ticket.paid_at >= one_year_ago
        ).scalar()
        sales = float(sales) if sales else 0.0

        # Средняя оценка отзывов за год
        avg_rating = db.query(func.avg(Review.rating)).join(
            Event, Review.event_id == Event.id
        ).filter(
            Event.venue_id == venue.id,
            Review.created_at >= one_year_ago
        ).scalar()
        avg_rating = float(avg_rating) if avg_rating else 0.0

        sales_score = sales / max_sales if max_sales > 0 else 0.0
        rating_score = avg_rating / 5.0 if avg_rating else 0.0
        rating = (sales_score * 0.6 + rating_score * 0.4) * 100
        rating = round(rating, 2)

        if rating > 0:
            result.append({
                'id': venue.id,
                'name': venue.name,
                'city': venue.city,
                'rating': rating,
                'image_url': f"https://via.placeholder.com/800x400?text={venue.name.replace(' ', '+')}"
            })

    result.sort(key=lambda x: x['rating'], reverse=True)
    return jsonify(result[:10])