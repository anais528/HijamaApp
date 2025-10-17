from flask import Flask 
#from flask_cors import CORS
from .config import Config
from .extensions import db
from datetime import timedelta

DB_NAME = "database.db"


def create_test_data(app):
    with app.app_context():
        from .models import Staff, Service
        db.drop_all()
        db.create_all()  # Create tables
        
        # Add test staff if table empty
        if not Staff.query.first():
            staff1 = Staff(name="Dr. Female", gender="female")
            staff2 = Staff(name="Dr. Male", gender="male")
            db.session.add_all([staff1, staff2])
            db.session.commit()
            print("Test staff data created.")
        
        # Add test services if table empty
        if not Service.query.first():
            service1 = Service(name="Basic Cupping", duration=timedelta(minutes=30))
            service2 = Service(name="Advanced Cupping", duration=timedelta(minutes=60))
            service3 = Service(name="Massage Therapy", duration=timedelta(minutes=45))
            db.session.add_all([service1, service2, service3])
            db.session.commit()
            print("Test services data created.")



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
