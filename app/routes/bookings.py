from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import get_db
from moduls.ticket import Ticket
from moduls.session import Session
from moduls.seat import Seat
from moduls.event import Event
from moduls.payment import Payment
from moduls.receipt import Receipt
from datetime import datetime, timedelta
import random
import string

bp = Blueprint('bookings', __name__)


@bp.route('/select_seats/<int:session_id>', methods=['GET', 'POST'])
@login_required
def select_seats(session_id):
    db = get_db()
    session = db.query(Session).get(session_id)
    if not session:
        return "Сеанс не найден", 404
    
    venue_id = session.event.venue_id
    # Получаем все места, сортируем по ряду и месту
    seats = db.query(Seat).filter_by(venue_id=venue_id, is_active=True).order_by(Seat.row_number, Seat.seat_number).all()
    
    # Получаем занятые места на этот сеанс
    taken = db.query(Ticket.seat_id).filter(Ticket.session_id == session_id, Ticket.status.in_(['pending', 'paid'])).all()
    taken_ids = {t[0] for t in taken}
    
    # Группируем места по рядам
    rows = {}
    for seat in seats:
        if seat.row_number not in rows:
            rows[seat.row_number] = []
        rows[seat.row_number].append(seat)
    
    # Находим максимальное количество мест в ряду (для таблицы)
    max_seats_in_row = max(len(seats_in_row) for seats_in_row in rows.values()) if rows else 0
    
    return render_template('bookings/select_seats.html',
                           session=session,
                           rows=rows,
                           taken_ids=taken_ids,
                           max_seats_in_row=max_seats_in_row)

@bp.route('/cancel/<int:ticket_id>')
@login_required
def cancel(ticket_id):
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        flash('Билет не найден.', 'danger')
        return redirect(url_for('profile.bookings'))
    
    if ticket.status == 'paid':
        flash('Нельзя отменить оплаченный билет.', 'warning')
    else:
        ticket.status = 'cancelled'
        db.commit()
        flash('Бронирование отменено.', 'info')
    return redirect(url_for('profile.bookings'))

@bp.route('/pay/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def pay(ticket_id):
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        flash('Билет не найден.', 'danger')
        return redirect(url_for('profile.bookings'))
    if ticket.status == 'paid':
        flash('Билет уже оплачен.', 'info')
        return redirect(url_for('profile.bookings'))
    
    # Подгружаем связанные объекты для отображения
    ticket.session = db.query(Session).get(ticket.session_id)
    if ticket.session:
        ticket.event = db.query(Event).get(ticket.session.event_id)
    ticket.seat = db.query(Seat).get(ticket.seat_id)
    
    if request.method == 'POST':
        from datetime import datetime
        ticket.status = 'paid'
        ticket.paid_at = datetime.now()
        
        from moduls.payment import Payment
        from moduls.receipt import Receipt
        import random, string
        
        payment = Payment(
            ticket_id=ticket.id,
            amount=ticket.price_paid,
            status='succeeded',
            payment_method='card',
            paid_at=datetime.now()
        )
        db.add(payment)
        db.flush()
        
        receipt_number = 'RCP-' + ''.join(random.choices(string.digits, k=10))
        receipt = Receipt(
            payment_id=payment.id,
            receipt_number=receipt_number,
            sent_to_email=False
        )
        db.add(receipt)
        db.commit()
        
        flash('Оплата прошла успешно! Чек сгенерирован.', 'success')
        return redirect(url_for('bookings.receipt', ticket_id=ticket.id))
    
    return render_template('payment/payment.html', ticket=ticket)

@bp.route('/receipt/<int:ticket_id>')
@login_required
def receipt(ticket_id):
    db = get_db()
    ticket = db.query(Ticket).get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        flash('Чек не найден.', 'danger')
        return redirect(url_for('profile.bookings'))
    payment = db.query(Payment).filter_by(ticket_id=ticket.id).first()
    if not payment:
        flash('Платёж не найден.', 'danger')
        return redirect(url_for('profile.bookings'))
    receipt = db.query(Receipt).filter_by(payment_id=payment.id).first()
    return render_template('payment/receipt.html', ticket=ticket, payment=payment, receipt=receipt)