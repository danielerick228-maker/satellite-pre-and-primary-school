#!/usr/bin/env python3
"""
Simple Database Connection Test
Run this to test if your database is working properly.
"""

from flask import Flask
from config import Config
from models import db, User

def test_db_connection():
    """Test basic database connectivity"""
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        print("🔍 Testing Database Connection...")
        print(f"📊 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Initialize database
        with app.app_context():
            db.init_app(app)
            
            # Test connection
            with db.engine.connect() as conn:
                conn.execute(db.text("SELECT 1"))
            print("✅ Database connection successful!")
            
            # Check tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Available tables: {tables}")
            
            # Test User model
            if 'user' in tables:
                print("✅ User table exists!")
                
                # Count users
                user_count = User.query.count()
                print(f"👥 Total users in database: {user_count}")
            else:
                print("❌ User table not found!")
                
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Satellite School - Database Connection Test")
    print("=" * 50)
    
    if test_db_connection():
        print("\n🎉 Database is working correctly!")
    else:
        print("\n❌ Database connection failed!")
        print("\n💡 Troubleshooting tips:")
        print("1. Make sure you've run: python init_database.py")
        print("2. Check if app.db file exists in your project folder")
        print("3. Verify all requirements are installed: pip install -r requirements.txt")
