#!/usr/bin/env python3
"""
Simple script to create the Application table
"""

from flask import Flask
from config import Config
from models import db, Application

def create_application_table():
    """Create the Application table"""
    try:
        # Create Flask app
        app = Flask(__name__)
        app.config.from_object(Config)
        
        print("🔧 Creating Application table...")
        
        with app.app_context():
            db.init_app(app)
            
            # Create the Application table
            Application.__table__.create(db.engine, checkfirst=True)
            print("✅ Application table created successfully!")
            
            # Verify table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"📋 Available tables: {tables}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Creating Application Table")
    print("=" * 40)
    
    if create_application_table():
        print("\n🎉 Table creation completed!")
        print("Now you can test your application form!")
    else:
        print("\n❌ Table creation failed!")
