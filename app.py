"""
This module contains the main application for the website. 
"""

from frontend import create_app 
app = create_app()

if __name__ == "__main__":
    app.run(debug=1)



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