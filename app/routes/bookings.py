from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.database import get_db
from moduls.session import Session
from moduls.seat import Seat
from moduls.ticket import Ticket
from datetime import datetime, timedelta
import random

bp = Blueprint('bookings', __name__)

@bp.route('/select_seats/<int:session_id>', methods=['GET', 'POST'])
@login_required
def select_seats(session_id):
    db = get_db()
    session = db.query(Session).get(session_id)
    if not session:
        return "Сеанс не найден", 404
    
    # Получаем все места площадки
    venue_id = session.event.venue_id
    seats = db.query(Seat).filter_by(venue_id=venue_id, is_active=True).order_by(Seat.row_number, Seat.seat_number).all()
    
    # Получаем уже занятые места на этот сеанс
    taken_seats = db.query(Ticket.seat_id).filter(Ticket.session_id == session_id, Ticket.status.in_(['pending', 'paid'])).all()
    taken_ids = [t[0] for t in taken_seats]
    
    if request.method == 'POST':
        selected_seat_ids = request.form.getlist('seat_ids')
        if not selected_seat_ids:
            flash('Выберите хотя бы одно место.', 'warning')
            return redirect(url_for('bookings.select_seats', session_id=session_id))
        
        # Создаём бронирование для каждого места
        for seat_id in selected_seat_ids:
            if int(seat_id) in taken_ids:
                flash(f'Место {seat_id} уже занято.', 'danger')
                return redirect(url_for('bookings.select_seats', session_id=session_id))
            
            ticket = Ticket(
                user_id=current_user.id,
                session_id=session_id,
                seat_id=seat_id,
                price_paid=session.base_price,
                status='pending',
                booking_expires_at=datetime.now() + timedelta(minutes=15),
                qr_code=None
            )
            db.add(ticket)
        db.commit()
        flash('Билеты забронированы! Оплатите в течение 15 минут.', 'success')
        return redirect(url_for('profile.bookings'))
    
    return render_template('bookings/select_seats.html', session=session, seats=seats, taken_ids=taken_ids)

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
    if request.method == 'POST':
        # Имитация оплаты
        from datetime import datetime
        ticket.status = 'paid'
        # Создаём запись платежа и чека
        from moduls.payment import Payment
        from moduls.receipt import Receipt
        import random, string
        payment = Payment(ticket_id=ticket.id, amount=ticket.price_paid, status='succeeded', 
                          payment_method='card', paid_at=datetime.now())
        db.add(payment)
        db.flush()
        receipt_number = 'RCP-' + ''.join(random.choices(string.digits, k=10))
        receipt = Receipt(payment_id=payment.id, receipt_number=receipt_number, sent_to_email=False)
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