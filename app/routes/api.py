from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.database import get_db
from moduls.event import Event
from moduls.session import Session
from moduls.seat import Seat
from moduls.ticket import Ticket
from moduls.review import Review
from moduls.payment import Payment
from datetime import datetime, timedelta
import random

from app.routes.weather import get_weather
from app.extensions import csrf

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/events')
def api_events():
    db = get_db()
    events = db.query(Event).all()
    return jsonify([{'id': e.id, 'title': e.title, 'category': e.category} for e in events])

@bp.route('/events/<int:event_id>')
def api_event_detail(event_id):
    db = get_db()
    e = db.query(Event).get(event_id)
    if not e:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'id': e.id, 'title': e.title, 'description': e.description, 'category': e.category})

@bp.route('/events/<int:event_id>/sessions')
def api_event_sessions(event_id):
    db = get_db()
    sessions = db.query(Session).filter_by(event_id=event_id, is_cancelled=False).all()
    return jsonify([{'id': s.id, 'start_time': s.start_time.isoformat(), 'price': float(s.base_price)} for s in sessions])

@bp.route('/sessions/<int:session_id>/seats')
def api_available_seats(session_id):
    db = get_db()
    taken = db.query(Ticket.seat_id).filter(Ticket.session_id == session_id, Ticket.status.in_(['pending','paid'])).all()
    taken_ids = [t[0] for t in taken]
    session = db.query(Session).get(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    seats = db.query(Seat).filter_by(venue_id=session.event.venue_id, is_active=True).all()
    result = [{'id': s.id, 'row': s.row_number, 'number': s.seat_number, 'available': s.id not in taken_ids} for s in seats]
    return jsonify(result)

@bp.route('/bookings', methods=['POST'])
@csrf.exempt
@login_required
def api_create_booking():
    data = request.get_json()
    session_id = data.get('session_id')
    seat_ids = data.get('seat_ids', [])
    db = get_db()
    session = db.query(Session).get(session_id)
    if not session:
        return jsonify({'error': 'Invalid session'}), 400
    tickets = []
    for seat_id in seat_ids:
        existing = db.query(Ticket).filter_by(session_id=session_id, seat_id=seat_id, status='paid').first()
        if existing:
            return jsonify({'error': f'Seat {seat_id} already taken'}), 409
        ticket = Ticket(user_id=current_user.id, session_id=session_id, seat_id=seat_id,
                        price_paid=session.base_price, status='pending',
                        booking_expires_at=datetime.now() + timedelta(minutes=15))
        db.add(ticket)
        tickets.append(ticket)
    db.commit()
    return jsonify({'message': 'Booked', 'ticket_ids': [t.id for t in tickets]}), 201

@bp.route('/bookings/<int:ticket_id>', methods=['GET'])
@login_required
def api_booking_status(ticket_id):
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'id': ticket.id, 'status': ticket.status, 'price': float(ticket.price_paid)})

@bp.route('/bookings/<int:ticket_id>', methods=['DELETE'])
@csrf.exempt
@login_required
def api_cancel_booking(ticket_id):
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        return jsonify({'error': 'Not found'}), 404
    if ticket.status == 'paid':
        return jsonify({'error': 'Cannot cancel paid ticket'}), 400
    ticket.status = 'cancelled'
    db.commit()
    return jsonify({'message': 'Cancelled'})

@bp.route('/payments', methods=['POST'])
@csrf.exempt
@login_required
def api_payment():
    data = request.get_json()
    ticket_id = data.get('ticket_id')
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        return jsonify({'error': 'Invalid ticket'}), 400
    if ticket.status == 'paid':
        return jsonify({'error': 'Already paid'}), 409
    # Имитация успешной оплаты
    ticket.status = 'paid'
    payment = Payment(ticket_id=ticket.id, amount=ticket.price_paid, status='succeeded',
                      payment_method='card', paid_at=datetime.now())
    db.add(payment)
    db.commit()
    return jsonify({'message': 'Payment succeeded', 'payment_id': payment.id})

@bp.route('/reviews', methods=['GET'])
def api_reviews():
    event_id = request.args.get('event_id')
    if not event_id:
        return jsonify({'error': 'event_id required'}), 400
    db = get_db()
    reviews = db.query(Review).filter_by(event_id=event_id).order_by(Review.created_at.desc()).all()
    return jsonify([{'id': r.id, 'rating': r.rating, 'comment': r.comment, 'user': r.user.full_name} for r in reviews])

@bp.route('/reviews/<int:review_id>', methods=['PUT'])
@csrf.exempt
@login_required
def api_update_review(review_id):
    data = request.get_json()
    db = get_db()
    review = db.query(Review).get(review_id)
    if not review:
        return jsonify({'error': 'Review not found'}), 404
    if review.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403

    rating = data.get('rating')
    comment = data.get('comment')

    if rating is not None:
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({'error': 'Rating must be 1-5'}), 400
        review.rating = rating
    if comment is not None:
        review.comment = comment

    db.commit()
    return jsonify({'message': 'Review updated', 'id': review.id, 'rating': review.rating})

@bp.route('/reviews', methods=['POST'])
@csrf.exempt
@login_required
def api_create_review():
    data = request.get_json()
    event_id = data.get('event_id')
    rating = data.get('rating')
    comment = data.get('comment')
    if not event_id or not rating:
        return jsonify({'error': 'Missing fields'}), 400
    db = get_db()
    existing = db.query(Review).filter_by(user_id=current_user.id, event_id=event_id).first()
    if existing:
        return jsonify({'error': 'Already reviewed'}), 409
    review = Review(user_id=current_user.id, event_id=event_id, rating=rating, comment=comment, is_verified=False)
    db.add(review)
    db.commit()
    return jsonify({'message': 'Review added'}), 201

@bp.route('/weather')
def api_weather():
    return jsonify(get_weather())