#!/usr/bin/env python3
"""
Database Initialization Script for Satellite Pre & Primary School
This script helps initialize and test the database connection.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def init_database():
    """Initialize the database and create tables"""
    try:
        print("🚀 Initializing Satellite School Database...")
        print("=" * 50)
        
        # Import Flask app components
        from flask import Flask
        from config import Config
        from models import db
        from database import init_db, init_migrations
        
        # Create a minimal Flask app for database operations
        app = Flask(__name__)
        app.config.from_object(Config)
        
        print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f"🔑 Secret Key: {'Set' if app.config['SECRET_KEY'] != 'your-secret-key-here-change-this' else 'Default (Please change)'}")
        
        # Initialize database
        with app.app_context():
            db.init_app(app)
            db.create_all()
            
            # Test database connection
            try:
                with db.engine.connect() as conn:
                    conn.execute(db.text("SELECT 1"))
                print("✅ Database connection successful!")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Check if tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Tables created: {', '.join(tables) if tables else 'None'}")
            
            if 'user' in tables:
                print("✅ User table created successfully!")
            else:
                print("❌ User table not found!")
                
        print("=" * 50)
        print("🎉 Database initialization completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database initialization: {e}")
        print("💡 Make sure you have installed all requirements:")
        print("   pip install -r requirements.txt")
        return False

def test_database_operations():
    """Test basic database operations"""
    try:
        print("\n🧪 Testing Database Operations...")
        print("=" * 30)
        
        from flask import Flask
        from config import Config
        from models import db, User
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            db.init_app(app)
            
            # Test user creation
            test_user = User(
                first_name="Test",
                last_name="User",
                email="test@example.com",
                phone="1234567890"
            )
            test_user.set_password("testpass123")
            
            # Add to database
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created successfully!")
            
            # Test user retrieval
            retrieved_user = User.query.filter_by(email="test@example.com").first()
            if retrieved_user:
                print(f"✅ User retrieved: {retrieved_user.get_full_name()}")
            else:
                print("❌ User retrieval failed!")
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            print("✅ Test user cleaned up!")
            
        print("✅ Database operations test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Satellite Pre & Primary School - Database Setup")
    print("=" * 60)
    
    # Initialize database
    if init_database():
        print("\n🔍 Running database tests...")
        test_database_operations()
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
    
    print("\n🎯 Next steps:")
    print("1. Run your Flask app: python app.py")
    print("2. Test user registration at /signup")
    print("3. Test user login at /login")
    print("4. Check database file: app.db (SQLite)")
