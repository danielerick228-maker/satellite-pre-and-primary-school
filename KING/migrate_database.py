#!/usr/bin/env python3
"""
Database Migration Script for Satellite Pre & Primary School
This script adds the new Application table to the existing database.
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def migrate_database():
    """Migrate the database to add new tables"""
    try:
        print("🚀 Migrating Satellite School Database...")
        print("=" * 50)
        
        # Import Flask app components
        from flask import Flask
        from config import Config
        from models import db, User, Application
        from database import init_db, init_migrations
        
        # Create a minimal Flask app for database operations
        app = Flask(__name__)
        app.config.from_object(Config)
        
        print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Initialize database
        with app.app_context():
            db.init_app(app)
            
            # Check existing tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            print(f"📋 Existing tables: {', '.join(existing_tables) if existing_tables else 'None'}")
            
            # Create new tables
            db.create_all()
            
            # Check tables after migration
            inspector = db.inspect(db.engine)
            updated_tables = inspector.get_table_names()
            print(f"📋 Tables after migration: {', '.join(updated_tables) if updated_tables else 'None'}")
            
            # Check if Application table was created
            if 'application' in updated_tables:
                print("✅ Application table created successfully!")
            else:
                print("❌ Application table not found!")
                
            # Check if User table exists
            if 'user' in updated_tables:
                print("✅ User table exists!")
                user_count = User.query.count()
                print(f"👥 Total users: {user_count}")
            else:
                print("❌ User table not found!")
                
        print("=" * 50)
        print("🎉 Database migration completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during database migration: {e}")
        return False

def test_application_model():
    """Test the Application model"""
    try:
        print("\n🧪 Testing Application Model...")
        print("=" * 30)
        
        from flask import Flask
        from config import Config
        from models import db, Application
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            db.init_app(app)
            
            # Test application creation
            test_application = Application(
                first_name="Test",
                surname="Student",
                nationality="Tanzanian",
                gender="Male",
                date_of_birth="2015-01-01",
                place_of_birth="Mwanza",
                father_first_name="Test",
                father_last_name="Father",
                father_occupation="Teacher",
                father_telephone="1234567890",
                father_address="Test Address",
                mother_first_name="Test",
                mother_last_name="Mother",
                mother_occupation="Nurse",
                mother_telephone="0987654321",
                mother_address="Test Address"
            )
            
            # Add to database
            db.session.add(test_application)
            db.session.commit()
            print("✅ Test application created successfully!")
            print(f"📝 Application ID: {test_application.id}")
            
            # Test application retrieval
            retrieved_app = Application.query.filter_by(id=test_application.id).first()
            if retrieved_app:
                print(f"✅ Application retrieved: {retrieved_app.get_student_name()}")
            else:
                print("❌ Application retrieval failed!")
            
            # Clean up test application
            db.session.delete(test_application)
            db.session.commit()
            print("✅ Test application cleaned up!")
            
        print("✅ Application model test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Application model test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Satellite Pre & Primary School - Database Migration")
    print("=" * 60)
    
    # Migrate database
    if migrate_database():
        print("\n🔍 Testing application functionality...")
        test_application_model()
    else:
        print("\n❌ Database migration failed!")
        sys.exit(1)
    
    print("\n🎯 Next steps:")
    print("1. Run your Flask app: python app.py")
    print("2. Test application form at /application")
    print("3. Submit an application to test the database")
    print("4. Check database file: app.db (SQLite)")
