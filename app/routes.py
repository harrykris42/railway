from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from app.forms import RegisterForm, LoginForm
from app.models import User, Train, Booking, db
from app import bcrypt
from datetime import datetime
import random
import string

def register_routes(app):
    def generate_ticket_id():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    @app.route('/')
    def index():
        return render_template('home.html')

    # REGISTER
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = RegisterForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(name=form.name.data).first()
            if existing_user:
                flash('❌ Username already exists.', 'danger')
            else:
                hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(name=form.name.data, password=hashed_pw)
                db.session.add(user)
                db.session.commit()
                flash('✅ Account created. You can now log in.', 'success')
                return redirect(url_for('login'))

        return render_template('register.html', form=form)

    # LOGIN
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))

        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('✅ Logged in successfully.', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('❌ Invalid username or password.', 'danger')
        return render_template('login.html', form=form)

    # LOGOUT
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    # DASHBOARD (with train list and user's bookings)
    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        filters = {}
        from_station = request.args.get('from_station')
        to_station = request.args.get('to_station')
        date = request.args.get('date')

        query = Train.query
        if from_station:
            query = query.filter(Train.from_station.ilike(f"%{from_station}%"))
        if to_station:
            query = query.filter(Train.to_station.ilike(f"%{to_station}%"))
        if date:
            query = query.filter(Train.date == date)

        trains = query.filter(Train.date >= datetime.now().date()).all()
        bookings = Booking.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', trains=trains, bookings=bookings)


    # Book a train
    @app.route('/book/<int:train_id>', methods=['POST'])
    @login_required
    def book(train_id):
        train = Train.query.get_or_404(train_id)
        seats = int(request.form['seats'])

        if train.available_seats >= seats:
            ticket = Booking(
                user_id=current_user.id,
                train_id=train.id,
                seats_booked=seats,
                travel_date=train.date,
                ticket_id=generate_ticket_id()
            )
            train.available_seats -= seats
            db.session.add(ticket)
            db.session.commit()
            flash('🎫 Booking successful!', 'success')
        else:
            flash('❌ Not enough seats available.', 'danger')

        return redirect(url_for('dashboard'))
    
    @app.route('/cancel/<int:booking_id>', methods=['POST'])
    @login_required
    def cancel_booking(booking_id):
        booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()
        if booking:
            train = Train.query.get(booking.train_id)
            train.available_seats += booking.seats_booked
            db.session.delete(booking)
            db.session.commit()
            flash('❌ Booking cancelled.', 'info')
        else:
            flash('Booking not found.', 'danger')
        return redirect(url_for('dashboard'))

    @app.route('/admin', methods=['GET', 'POST'])
    @login_required
    def admin_panel():
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))

        if request.method == 'POST':
            new_train = Train(
                train_name=request.form['train_name'],
                from_station=request.form['from_station'],
                to_station=request.form['to_station'],
                total_seats=int(request.form['total_seats']),
                available_seats=int(request.form['total_seats']),
                date=request.form['date']
            )
            db.session.add(new_train)
            db.session.commit()
            flash('✅ Train added.', 'success')
            return redirect(url_for('admin_panel'))

        trains = Train.query.order_by(Train.date).all()
        return render_template('admin.html', trains=trains)

    @app.route('/admin/delete/<int:train_id>', methods=['POST'])
    @login_required
    def delete_train(train_id):
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))

        train = Train.query.get_or_404(train_id)
        db.session.delete(train)
        db.session.commit()
        flash('🚮 Train deleted.', 'info')
        return redirect(url_for('admin_panel'))

    @app.route('/admin/edit/<int:train_id>', methods=['POST'])
    @login_required
    def edit_train(train_id):
        if not current_user.is_admin:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))

        train = Train.query.get_or_404(train_id)
        train.train_name = request.form['train_name']
        train.from_station = request.form['from_station']
        train.to_station = request.form['to_station']
        train.total_seats = int(request.form['total_seats'])
        train.available_seats = train.total_seats  # Optionally keep this unchanged
        train.date = request.form['date']
        db.session.commit()
        flash('✅ Train updated.', 'success')
        return redirect(url_for('admin_panel'))
