from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__, static_folder='.', template_folder='.')
CORS(app)  # Enable CORS for all routes

# Sample data for your app
bookings = []
analytics_data = {
    'total_bookings': 0,
    'monthly_revenue': 0,
    'popular_services': []
}

@app.route('/')
def home():
    """Main homepage - renders index.html"""
    try:
        return render_template('index.html')
    except:
        return """
        <h1>Hijama App - Home</h1>
        <nav>
            <a href="/booking">Book Appointment</a> |
            <a href="/analytics">Analytics</a> |
            <a href="/contact">Contact</a>
        </nav>
        <p>Welcome to the Hijama App!</p>
        <p>Please make sure your HTML files are in the correct location.</p>
        """

@app.route('/booking')
def booking():
    """Booking page - renders booking.html"""
    try:
        return render_template('booking.html')
    except:
        return """
        <h1>Book Your Hijama Appointment</h1>
        <nav><a href="/">Home</a> | <a href="/analytics">Analytics</a> | <a href="/contact">Contact</a></nav>
        <form method="POST" action="/api/booking">
            <p><label>Name: <input type="text" name="name" required></label></p>
            <p><label>Email: <input type="email" name="email" required></label></p>
            <p><label>Phone: <input type="tel" name="phone" required></label></p>
            <p><label>Preferred Date: <input type="date" name="date" required></label></p>
            <p><label>Preferred Time: <input type="time" name="time" required></label></p>
            <p><label>Service Type: 
                <select name="service" required>
                    <option value="">Select Service</option>
                    <option value="hijama-dry">Dry Hijama</option>
                    <option value="hijama-wet">Wet Hijama</option>
                    <option value="hijama-massage">Hijama + Massage</option>
                </select>
            </label></p>
            <p><label>Notes: <textarea name="notes" rows="3"></textarea></label></p>
            <p><button type="submit">Book Appointment</button></p>
        </form>
        """

@app.route('/analytics')
def analytics():
    """Analytics page - renders analytics.html"""
    try:
        return render_template('analytics.html')
    except:
        return f"""
        <h1>Hijama App Analytics</h1>
        <nav><a href="/">Home</a> | <a href="/booking">Book</a> | <a href="/contact">Contact</a></nav>
        <div>
            <h2>Dashboard Overview</h2>
            <p><strong>Total Bookings:</strong> {len(bookings)}</p>
            <p><strong>This Month:</strong> {sum(1 for b in bookings if b.get('status') == 'confirmed')}</p>
            <p><strong>Revenue:</strong> ${analytics_data['monthly_revenue']}</p>
            
            <h3>Recent Bookings</h3>
            <ul>
                {chr(10).join([f"<li>{b.get('name', 'Unknown')} - {b.get('service', 'N/A')} - {b.get('date', 'TBD')}</li>" for b in bookings[-5:]])}
            </ul>
        </div>
        """

@app.route('/contact')
def contact():
    """Contact page - renders contact.html"""
    try:
        return render_template('contact.html')
    except:
        return """
        <h1>Contact Us</h1>
        <nav><a href="/">Home</a> | <a href="/booking">Book</a> | <a href="/analytics">Analytics</a></nav>
        <div>
            <h2>Get in Touch</h2>
            <p><strong>Phone:</strong> +1 (555) 123-4567</p>
            <p><strong>Email:</strong> info@hijamaapp.com</p>
            <p><strong>Address:</strong> 123 Wellness Street, Health City, HC 12345</p>
            
            <h3>Send us a message</h3>
            <form method="POST" action="/api/contact">
                <p><label>Name: <input type="text" name="name" required></label></p>
                <p><label>Email: <input type="email" name="email" required></label></p>
                <p><label>Subject: <input type="text" name="subject" required></label></p>
                <p><label>Message: <textarea name="message" rows="5" required></textarea></label></p>
                <p><button type="submit">Send Message</button></p>
            </form>
            
            <h3>Business Hours</h3>
            <ul>
                <li>Monday - Friday: 9:00 AM - 7:00 PM</li>
                <li>Saturday: 10:00 AM - 5:00 PM</li>
                <li>Sunday: Closed</li>
            </ul>
        </div>
        """

# API Routes for handling form submissions and data

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'message': 'Hijama App backend is running'
    })

@app.route('/api/booking', methods=['POST'])
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

@app.route('/api/contact', methods=['POST'])
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

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Get all bookings (for analytics)"""
    return jsonify({
        'bookings': bookings,
        'count': len(bookings),
        'analytics': analytics_data
    })

@app.route('/api/analytics', methods=['GET'])
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
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    """Serve files from frontend folder"""
    return send_from_directory('frontend', filename)

# Handle any additional static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return """
    <h1>Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <nav>
        <a href="/">Home</a> |
        <a href="/booking">Book Appointment</a> |
        <a href="/analytics">Analytics</a> |
        <a href="/contact">Contact</a>
    </nav>
    """, 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Use environment variables for configuration
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Hijama App Server...")
    print(f"📱 Main App: http://localhost:{port}")
    print(f"📅 Booking: http://localhost:{port}/booking")
    print(f"📊 Analytics: http://localhost:{port}/analytics")
    print(f"📞 Contact: http://localhost:{port}/contact")
    print(f"🔧 API Health: http://localhost:{port}/api/health")
    
    app.run(host='0.0.0.0', port=port, debug=debug)