from flask_migrate import Migrate
from models import db
import os

def init_db(app):
    """Initialize the database with the Flask app"""
    try:
        db.init_app(app)
        
        # Create all tables
        with app.app_context():
            db.create_all()
            print("✅ Database initialized successfully!")
            print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
        return db
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise e

def init_migrations(app):
    """Initialize Flask-Migrate for database migrations"""
    try:
        migrate = Migrate(app, db)
        print("✅ Database migrations initialized successfully!")
        return migrate
    except Exception as e:
        print(f"❌ Error initializing migrations: {e}")
        raise e

def create_tables():
    """Create database tables manually if needed"""
    try:
        from models import User
        db.create_all()
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise e
