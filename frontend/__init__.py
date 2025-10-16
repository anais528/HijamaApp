from flask import Flask 
#from flask_cors import CORS
from .config import Config
from .extensions import db

DB_NAME = "database.db"


# Temporary populating the tables with test data
def create_test_data(app):
    with app.app_context():
        from .models import Client, Staff, Appointment  # Import models here
        
        db.create_all()  # Create tables
        
        # Add test clients if table empty
        if not Client.query.first():
            client1 = Client(name="Alice", contact_info="alice@example.com", gender="female")
            client2 = Client(name="Bob", contact_info="bob@example.com", gender="male")
            db.session.add_all([client1, client2])
            
            staff1 = Staff(name="Dr. Female", gender="female")
            staff2 = Staff(name="Dr. Male", gender="male")
            db.session.add_all([staff1, staff2])
            
            db.session.commit()
            
            # Add an appointment
            appointment = Appointment(client_id=client1.id, staff_id=staff1.id, appointment_time="2025-10-20 10:00:00", status="booked")
            db.session.add(appointment)
            db.session.commit()
            
            print("Test data created.")


def create_app():
    app = Flask(__name__)
    #CORS(app)  # Enable CORS for all routes
    
    app.config.from_object(Config)
    db.init_app(app)
    
    # Import models after initializing db
    from . import models
    
    # Create test data during development
    create_test_data(app)
    
    # Register routes
    from .view import views 
    app.register_blueprint(views, url_prefix="/")
       
    return app
