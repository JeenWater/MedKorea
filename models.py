# models.py
from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Patient(db.patients):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    insurance = db.Column(db.String(10))
    preferred_language = db.Column(db.String(20))
    address = db.Column(db.String(100), nullable=False)
    medical_history = db.Column(db.Text)
    comments_for_doctor = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Patient {self.email}>'

class Doctor(db.doctors):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    birth = db.Column(db.Date, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    specialization = db.Column(db.String(50), nullable=False)
    license_number = db.Column(db.String(10), unique=True, nullable=False)
    medical_school = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.Text)
    address = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
