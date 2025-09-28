#!/usr/bin/env python3
"""
Initialize Admin User for Satellite Pre & Primary School
This script creates the default admin user with full permissions.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app import create_app
from models import db, Admin
from datetime import datetime

def init_admin():
    """Initialize the default admin user"""
    try:
        print("🔧 Initializing Admin User...")
        print("=" * 50)
        
        app = create_app()
        
        with app.app_context():
            # Check if admin already exists
            from config import Config
            target_email = Config.ADMIN_LOGIN_EMAIL
            existing_admin = Admin.query.filter_by(email=target_email).first()
            
            if existing_admin:
                print("✅ Admin user already exists!")
                print(f"Email: {existing_admin.email}")
                print(f"Role: {existing_admin.role}")
                print(f"Last Login: {existing_admin.last_login}")
                return True
            
            # Create new admin user
            admin = Admin(
                email=target_email,
                full_name='System Administrator',
                role='super_admin',
                permissions=None,  # Super admin has all permissions
                is_active=True
            )
            
            # Set password
            admin.set_password('admin123')
            
            # Add to database
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print(f"Email: {admin.email}")
            print(f"Password: admin123")
            print(f"Role: {admin.role}")
            print(f"Full Name: {admin.full_name}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def create_additional_admins():
    """Create additional admin users with specific permissions"""
    try:
        print("\n🔧 Creating Additional Admin Users...")
        print("=" * 50)
        
        app = create_app()
        
        with app.app_context():
            # Admissions Officer
            admissions_officer = Admin.query.filter_by(email='admissions@satellite.ac.tz').first()
            if not admissions_officer:
                admissions_officer = Admin(
                    email='admissions@satellite.ac.tz',
                    full_name='Admissions Officer',
                    role='admin',
                    permissions='["view_applications", "approve_applications", "reject_applications", "view_payments", "export_data"]',
                    is_active=True
                )
                admissions_officer.set_password('admissions123')
                db.session.add(admissions_officer)
                print("✅ Admissions Officer created")
            
            # Finance Officer
            finance_officer = Admin.query.filter_by(email='finance@satellite.ac.tz').first()
            if not finance_officer:
                finance_officer = Admin(
                    email='finance@satellite.ac.tz',
                    full_name='Finance Officer',
                    role='admin',
                    permissions='["view_payments", "manage_payments", "view_reports", "export_financial_data"]',
                    is_active=True
                )
                finance_officer.set_password('finance123')
                db.session.add(finance_officer)
                print("✅ Finance Officer created")
            
            # Principal
            principal = Admin.query.filter_by(email='principal@satellite.ac.tz').first()
            if not principal:
                principal = Admin(
                    email='principal@satellite.ac.tz',
                    full_name='School Principal',
                    role='admin',
                    permissions='["view_applications", "approve_applications", "reject_applications", "view_payments", "view_reports", "manage_users", "export_data"]',
                    is_active=True
                )
                principal.set_password('principal123')
                db.session.add(principal)
                print("✅ Principal created")
            
            db.session.commit()
            print("✅ All additional admin users created successfully!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error creating additional admin users: {e}")
        return False

if __name__ == "__main__":
    print("🏫 Satellite Pre & Primary School - Admin Initialization")
    print("=" * 70)
    
    # Initialize main admin
    if init_admin():
        # Create additional admin users
        create_additional_admins()
        
        print("\n🎯 Admin Users Created:")
        print("1. admin@satellite.ac.tz (Super Admin) - admin123")
        print("2. admissions@satellite.ac.tz (Admissions) - admissions123")
        print("3. finance@satellite.ac.tz (Finance) - finance123")
        print("4. principal@satellite.ac.tz (Principal) - principal123")
        
        print("\n🔐 Login URLs:")
        print("- Admin Login: /admin/login")
        print("- User Login: /login")
        
        print("\n📋 Admin Permissions:")
        print("- Super Admin: Full access to all features")
        print("- Admissions Officer: Manage applications and payments")
        print("- Finance Officer: Manage payments and financial reports")
        print("- Principal: Full access except user management")
    else:
        print("\n❌ Admin initialization failed!")
        sys.exit(1)

