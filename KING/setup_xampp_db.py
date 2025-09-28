#!/usr/bin/env python3
"""
XAMPP Database Setup Script for Satellite Pre & Primary School
This script sets up the MySQL database in XAMPP for the school system.
"""

import pymysql
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def create_database():
    """Create the satellite_school database"""
    try:
        print("🚀 Setting up XAMPP MySQL Database...")
        print("=" * 50)
        
        # Connect to MySQL server (root user, no password by default in XAMPP)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS special CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database 'special' created successfully!")
        
        # Use the database
        cursor.execute("USE special")
        print("✅ Using database 'special'")
        
        # Create tables
        create_tables(cursor)
        
        cursor.close()
        connection.close()
        
        print("=" * 50)
        print("🎉 XAMPP Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n💡 Make sure XAMPP is running and MySQL service is started!")
        return False

def create_tables(cursor):
    """Create the necessary tables"""
    try:
        print("\n🔧 Creating database tables...")
        
        # User table
        user_table = """
        CREATE TABLE IF NOT EXISTS user (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50),
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            phone VARCHAR(20) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(user_table)
        print("✅ User table created successfully!")
        
        # Application table
        application_table = """
        CREATE TABLE IF NOT EXISTS application (
            id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            second_name VARCHAR(50),
            surname VARCHAR(50) NOT NULL,
            nationality VARCHAR(50) NOT NULL,
            gender VARCHAR(20) NOT NULL,
            religion VARCHAR(50),
            date_of_birth DATE NOT NULL,
            place_of_birth VARCHAR(100) NOT NULL,
            father_first_name VARCHAR(50) NOT NULL,
            father_second_name VARCHAR(50),
            father_last_name VARCHAR(50) NOT NULL,
            father_occupation VARCHAR(100) NOT NULL,
            father_nida VARCHAR(50),
            father_telephone VARCHAR(20) NOT NULL,
            father_address TEXT NOT NULL,
            father_street VARCHAR(100),
            father_photo VARCHAR(255),
            mother_first_name VARCHAR(50) NOT NULL,
            mother_second_name VARCHAR(50),
            mother_last_name VARCHAR(50) NOT NULL,
            mother_occupation VARCHAR(100) NOT NULL,
            mother_nida VARCHAR(50),
            mother_telephone VARCHAR(20) NOT NULL,
            mother_address TEXT NOT NULL,
            mother_street VARCHAR(100),
            mother_photo VARCHAR(255),
            guardian_first_name VARCHAR(50),
            guardian_last_name VARCHAR(50),
            guardian_occupation VARCHAR(100),
            guardian_telephone VARCHAR(20),
            guardian_address TEXT,
            guardian_photo VARCHAR(255),
            status VARCHAR(20) DEFAULT 'pending',
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_student_name (first_name, surname),
            INDEX idx_status (status),
            INDEX idx_submitted_at (submitted_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(application_table)
        print("✅ Application table created successfully!")
        
        # Show table information
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📋 Available tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise e

def test_connection():
    """Test the database connection"""
    try:
        print("\n🧪 Testing database connection...")
        
        from flask import Flask
        from config import Config
        from models import db, User, Application
        
        app = Flask(__name__)
        app.config.from_object(Config)
        
        with app.app_context():
            db.init_app(app)
            
            # Test connection
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT 1"))
                print("✅ Database connection successful!")
            
            # Test User model
            user_count = User.query.count()
            print(f"👥 Users in database: {user_count}")
            
            # Test Application model
            app_count = Application.query.count()
            print(f"📝 Applications in database: {app_count}")
            
        print("✅ Database connection test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Satellite Pre & Primary School - XAMPP Database Setup")
    print("=" * 70)
    
    # Setup database
    if create_database():
        print("\n🔍 Testing database functionality...")
        test_connection()
    else:
        print("\n❌ Database setup failed!")
        sys.exit(1)
    
    print("\n🎯 Next steps:")
    print("1. Install MySQL connector: pip install -r requirements.txt")
    print("2. Run your Flask app: python app.py")
    print("3. Test application form at /application")
    print("4. Check XAMPP phpMyAdmin to view your database")
