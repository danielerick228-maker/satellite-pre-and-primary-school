from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import Numeric

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        # Prefix with type to distinguish from Admin in Flask-Login session
        return f"user:{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    # Relationships
    applications = db.relationship('Application', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='admin')  # admin, super_admin
    permissions = db.Column(db.Text)  # JSON string of permissions
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        # Prefix with type to distinguish from User in Flask-Login session
        return f"admin:{self.id}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def has_permission(self, permission):
        if not self.permissions:
            return True  # Super admin has all permissions
        import json
        try:
            perms = json.loads(self.permissions)
            return permission in perms
        except:
            return True
    
    def get_full_name(self):
        return self.full_name
    
    def __repr__(self):
        return f'<Admin {self.email}>'

class Payment(db.Model):
    __tablename__ = 'payment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(Numeric(10, 2), nullable=False, default=10000.00)  # Tsh 10,000
    payment_method = db.Column(db.String(50), nullable=False)  # mpesa, tigo_pesa, airtel_money, etc.
    transaction_id = db.Column(db.String(100), unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationships
    application = db.relationship('Application', backref='payments')
    user = db.relationship('User', backref='payments')
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'

class Application(db.Model):
    __tablename__ = 'application'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Student Information
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(50))
    surname = db.Column(db.String(50), nullable=False)
    nationality = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    religion = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date, nullable=False)
    place_of_birth = db.Column(db.String(100), nullable=False)
    
    # Father's Information
    father_first_name = db.Column(db.String(50), nullable=False)
    father_second_name = db.Column(db.String(50))
    father_last_name = db.Column(db.String(50), nullable=False)
    father_occupation = db.Column(db.String(100), nullable=False)
    father_nida = db.Column(db.String(50))
    father_telephone = db.Column(db.String(20), nullable=False)
    father_address = db.Column(db.Text, nullable=False)
    father_street = db.Column(db.String(100))
    father_photo = db.Column(db.String(255))  # File path
    
    # Mother's Information
    mother_first_name = db.Column(db.String(50), nullable=False)
    mother_second_name = db.Column(db.String(50))
    mother_last_name = db.Column(db.String(50), nullable=False)
    mother_occupation = db.Column(db.String(100), nullable=False)
    mother_nida = db.Column(db.String(50))
    mother_telephone = db.Column(db.String(20), nullable=False)
    mother_address = db.Column(db.Text, nullable=False)
    mother_street = db.Column(db.String(100))
    mother_photo = db.Column(db.String(255))  # File path
    
    # Guardian's Information (Optional)
    guardian_first_name = db.Column(db.String(50))
    guardian_last_name = db.Column(db.String(50))
    guardian_occupation = db.Column(db.String(100))
    guardian_telephone = db.Column(db.String(20))
    guardian_address = db.Column(db.Text)
    guardian_photo = db.Column(db.String(255))  # File path
    
    # Application Metadata
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    payment_required = db.Column(db.Boolean, default=True)
    payment_completed = db.Column(db.Boolean, default=False)
    
    def get_student_name(self):
        if self.second_name:
            return f"{self.first_name} {self.second_name} {self.surname}"
        return f"{self.first_name} {self.surname}"
    
    def has_paid(self):
        return self.payment_completed or any(payment.status == 'completed' for payment in self.payments)
    
    def __repr__(self):
        return f'<Application {self.get_student_name()}>'
