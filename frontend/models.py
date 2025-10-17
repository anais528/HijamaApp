from datetime import time 
from frontend.extensions import db

class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.Enum('male', 'female', name='gender_enum'), nullable=False)

    appointments = db.relationship('Appointment', back_populates='client')

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('male', 'female', name='gender_enum'), nullable=False)
    # email and password for authentication later 
    
    appointments = db.relationship('Appointment', back_populates='staff')
    availabilities = db.relationship('StaffAvailability', back_populates='staff')

class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)  # new end time calculated from duration
    status = db.Column(db.String(50), default='booked')
    notes = db.Column(db.Text)
    
    client = db.relationship('Client', back_populates='appointments')
    staff = db.relationship('Staff', back_populates='appointments')


class StaffAvailability(db.Model):
    __tablename__ = 'staff_availabilities'
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0=Monday ... 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    staff = db.relationship('Staff', back_populates='availabilities')


class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Interval, nullable=False)  # duration stored as interval


class RoundRobinTracker(db.Model):
    __tablename__ = 'round_robin_tracker'
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.Enum('male', 'female', name='gender_enum'), unique=True, nullable=False)
    last_assigned_staff_id = db.Column(db.Integer, nullable=True)