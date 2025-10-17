from flask import Blueprint, render_template, jsonify, request, send_from_directory, redirect, url_for, flash
import os
from datetime import datetime
from datetime import timedelta

from .models import Client, Staff, Appointment, StaffAvailability, Service, RoundRobinTracker

from .extensions import db
import random


views = Blueprint("views", __name__)

@views.route('/healthz')
def healthz():
    return jsonify({'status': 'ok'}), 200

# Sample data for your app
bookings = []
analytics_data = {
    'total_bookings': 0,
    'monthly_revenue': 0,
    'popular_services': []
}

# ============================================
# PUBLIC ROUTES
# ============================================

@views.route('/')
def home():
    """Main homepage - renders landing page"""
    return render_template('batoul.html')


def get_available_staff(gender, appointment_time, total_duration):
    weekday = appointment_time.weekday()
    start_time = appointment_time.time()
    end_time = (appointment_time + total_duration).time()

    staff_list = Staff.query.filter_by(gender=gender).all()

    available_staff = []
    for staff in staff_list:
        availability = StaffAvailability.query.filter_by(
            staff_id=staff.id,
            weekday=weekday
        ).filter(
            StaffAvailability.start_time <= start_time,
            StaffAvailability.end_time >= end_time
        ).first()

        if not availability:
            continue

        overlap = Appointment.query.filter(
            Appointment.staff_id == staff.id,
            Appointment.appointment_time < appointment_time + total_duration,
            Appointment.end_time > appointment_time
        ).first()

        if not overlap:
            available_staff.append(staff)

    if not available_staff:
        return None

    # Round robin assignment
    tracker = RoundRobinTracker.query.filter_by(gender=gender).first()
    if not tracker:
        tracker = RoundRobinTracker(gender=gender, last_assigned_staff_id=None)
        db.session.add(tracker)
        db.session.commit()

    last_id = tracker.last_assigned_staff_id
    idx = 0
    if last_id:
        for i, staff in enumerate(available_staff):
            if staff.id == last_id:
                idx = (i + 1) % len(available_staff)
                break

    staff_to_assign = available_staff[idx]
    tracker.last_assigned_staff_id = staff_to_assign.id
    db.session.commit()
    return staff_to_assign


@views.route('/book', methods=['GET', 'POST'])
def book_appointment():
    services = Service.query.all()

    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']
        gender = request.form['gender']
        appointment_time = datetime.fromisoformat(request.form['appointment_time'])
        service_ids = request.form.getlist('services')

        client = Client.query.filter_by(name=name, contact_info=contact_info, gender=gender).first()
        if not client:
            client = Client(name=name, contact_info=contact_info, gender=gender)
            db.session.add(client)
            db.session.commit()

        total_duration = timedelta()
        for s_id in service_ids:
            service = Service.query.get(int(s_id))
            total_duration += service.duration

        # Automatically assign staff
        available_staff_member = get_available_staff(gender, appointment_time, total_duration)
        if not available_staff_member:
            flash("No staff available at the requested time. Please try a different time.")
            return redirect(url_for('views.book_appointment'))

        staff_id = available_staff_member.id
        end_time = appointment_time + total_duration

        # Create appointment
        appt = Appointment(
            client_id=client.id,
            staff_id=staff_id,
            appointment_time=appointment_time,
            end_time=end_time,
            status='booked'
        )
        db.session.add(appt)
        db.session.commit()
        flash(f"Appointment booked with {available_staff_member.name}!")
        return redirect(url_for('views.book_appointment'))

    return render_template('bookingtest.html', services=services)




@views.route('/landingpage')
def landingpage():
    """Landing page route"""
    return render_template('landing/landingpage.html')

@views.route('/booking2')
def booking():
    """Booking page"""
    return render_template('booking/booking.html')


@views.route('/contact')
def contact():
    """Contact page"""
    return render_template('landing/contact.html')


@views.route('/faq')
def faq():
    """FAQ page"""
    return render_template('landing/faq.html')

@views.route('/services')
def services():
    """Service details page"""
    return render_template('landing/service_details.html')

@views.route('/service-details')
def service_details():
    """Alternative route for service details"""
    return render_template('landing/service_details.html')

# ============================================
# ADMIN ROUTES
# ============================================

@views.route('/admin/login')
def admin_login():
    """Admin login page"""
    return render_template('admin/admin_login.html')

@views.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    # TODO: Add authentication check
    return render_template('admin/admin_dashboard.html')

@views.route('/admin/bookings')
def admin_bookings():
    """Admin booking management page"""
    # TODO: Add authentication check
    return render_template('admin/booking_management.html')

@views.route('/admin/analytics')
def admin_analytics():
    """Admin analytics dashboard"""
    # TODO: Add authentication check
    return render_template('admin/analytics_dashboard.html')

@views.route('/admin/content')
def admin_content():
    """Admin content management page"""
    # TODO: Add authentication check
    return render_template('admin/content_management.html')


# @views.route('/booking')
# def booking():
#     """Booking page - renders booking.html"""
#     try:
#         return render_template('booking.html')
#     except:
#         return """
#         <h1> Book Your Hijama Appointment </h1>
#         <nav><a href="/">Home</a> | <a href="/analytics">Analytics</a> | <a href="/contact">Contact</a></nav>
#         <form method="POST" action="/api/booking">
#             <p><label>Name: <input type="text" name="name" required></label></p>
#             <p><label>Email: <input type="email" name="email" required></label></p>
#             <p><label>Phone: <input type="tel" name="phone" required></label></p>
#             <p><label>Preferred Date: <input type="date" name="date" required></label></p>
#             <p><label>Preferred Time: <input type="time" name="time" required></label></p>
#             <p><label>Service Type: 
#                 <select name="service" required>
#                     <option value="">Select Service</option>
#                     <option value="hijama-dry">Dry Hijama</option>
#                     <option value="hijama-wet">Wet Hijama</option>
#                     <option value="hijama-massage">Hijama + Massage</option>
#                 </select>
#             </label></p>
#             <p><label>Notes: <textarea name="notes" rows="3"></textarea></label></p>
#             <p><button type="submit">Book Appointment</button></p>
#         </form>
#         """

# @views.route('/analytics')
# def analytics():
#     """Analytics page - renders analytics.html"""
#     try:
#         return render_template('analytics.html')
#     except:
#         return f"""
#         <h1>Hijama App Analytics</h1>
#         <nav><a href="/">Home</a> | <a href="/booking">Book</a> | <a href="/contact">Contact</a></nav>
#         <div>
#             <h2>Dashboard Overview</h2>
#             <p><strong>Total Bookings:</strong> {len(bookings)}</p>
#             <p><strong>This Month:</strong> {sum(1 for b in bookings if b.get('status') == 'confirmed')}</p>
#             <p><strong>Revenue:</strong> ${analytics_data['monthly_revenue']}</p>
            
#             <h3>Recent Bookings</h3>
#             <ul>
#                 {chr(10).join([f"<li>{b.get('name', 'Unknown')} - {b.get('service', 'N/A')} - {b.get('date', 'TBD')}</li>" for b in bookings[-5:]])}
#             </ul>
#         </div>
#         """



# API Routes for handling form submissions and data

@views.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Hijama App backend is running'
    })

@views.route('/api/booking', methods=['POST'])
def create_booking():
    """Handle booking form submission"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # Basic validation
        required_fields = ['name', 'email', 'phone', 'date', 'time', 'service']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create booking
        booking = {
            'id': len(bookings) + 1,
            'name': data['name'],
            'email': data['email'],
            'phone': data['phone'],
            'date': data['date'],
            'time': data['time'],
            'service': data['service'],
            'notes': data.get('notes', ''),
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        bookings.append(booking)
        
        # Update analytics
        analytics_data['total_bookings'] = len(bookings)
        
        if request.is_json:
            return jsonify({'booking': booking, 'message': 'Booking created successfully'}), 201
        else:
            return f"""
            <h1>Booking Confirmed!</h1>
            <p>Thank you {data['name']}, your booking has been confirmed.</p>
            <p><strong>Date:</strong> {data['date']} at {data['time']}</p>
            <p><strong>Service:</strong> {data['service']}</p>
            <p><a href="/booking">Book Another Appointment</a> | <a href="/">Home</a></p>
            """
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.route('/api/contact', methods=['POST'])
def handle_contact():
    """Handle contact form submission"""
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # In a real app, you'd send an email or store in database
        contact_message = {
            'name': data.get('name'),
            'email': data.get('email'),
            'subject': data.get('subject'),
            'message': data.get('message'),
            'timestamp': datetime.now().isoformat()
        }
        
        if request.is_json:
            return jsonify({'message': 'Contact form submitted successfully', 'data': contact_message}), 201
        else:
            return f"""
            <h1>Message Sent!</h1>
            <p>Thank you {data.get('name')}, we've received your message and will get back to you soon.</p>
            <p><a href="/contact">Send Another Message</a> | <a href="/">Home</a></p>
            """
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings (for analytics)"""
    return jsonify({
        'bookings': bookings,
        'count': len(bookings),
        'analytics': analytics_data
    })

@views.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    # Calculate some basic analytics
    total_bookings = len(bookings)
    confirmed_bookings = sum(1 for b in bookings if b.get('status') == 'confirmed')
    pending_bookings = sum(1 for b in bookings if b.get('status') == 'pending')
    
    # Service popularity
    services = {}
    for booking in bookings:
        service = booking.get('service', 'Unknown')
        services[service] = services.get(service, 0) + 1
    
    popular_services = sorted(services.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'popular_services': popular_services,
        'monthly_revenue': analytics_data['monthly_revenue'],
        'recent_bookings': bookings[-10:]  # Last 10 bookings
    })

# Static file serving for frontend folder
@views.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve files from frontend folder"""
    return send_from_directory('frontend', filename)

# Handle any additional static files
@views.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@views.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return """
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <nav>
        <a href="/">Home</a> |
        <a href="/booking">Book viewsointment</a> |
        <a href="/analytics">Analytics</a> |
        <a href="/contact">Contact</a>
    </nav>
    """, 404

@views.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500