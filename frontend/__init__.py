from flask import Flask 
#from flask_cors import CORS
from .config import Config
from .extensions import db
from datetime import timedelta, time 

DB_NAME = "database.db"


def create_test_data(app):
    with app.app_context():
        from .models import Staff, Service, StaffAvailability

        from datetime import time, timedelta

        db.drop_all()
        db.create_all()  # Create tables
        
        # Add test staff if table empty
        if not Staff.query.first():
            staff1 = Staff(name="Dr. Female", gender="female")
            staff2 = Staff(name="Dr. Male", gender="male")
            staff3 = Staff(name="Dr. New Male", gender="male")  # New male staff
            db.session.add_all([staff1, staff2, staff3])
            db.session.commit()

            # Availability for staff1 (Female) Mon-Fri 9am-5pm
            for wd in range(5):
                avail = StaffAvailability(
                    staff_id=staff1.id,
                    weekday=wd,
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
                db.session.add(avail)

            # Availability for staff2 (Male) Tue-Sat 10am-6pm
            for wd in range(1, 6):
                avail = StaffAvailability(
                    staff_id=staff2.id,
                    weekday=wd,
                    start_time=time(10, 0),
                    end_time=time(18, 0)
                )
                db.session.add(avail)

            # Availability for new male staff3 Wed-Sun 8am-4pm
            for wd in range(2, 7):
                avail = StaffAvailability(
                    staff_id=staff3.id,
                    weekday=wd,
                    start_time=time(8, 0),
                    end_time=time(16, 0)
                )
                db.session.add(avail)

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
