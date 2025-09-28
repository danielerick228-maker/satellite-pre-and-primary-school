from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import re
import uuid
from datetime import datetime
from config import Config
from models import db, User, Application, Admin, Payment
from database import init_db, init_migrations

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database and migrations
    init_db(app)
    init_migrations(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Your existing routes
    @app.route("/")
    def home():
        return render_template("announcement.html")
    
    @app.route("/original-home")
    def original_home():
        return render_template("index.html")
    
    @app.route("/about")
    def about():
        return render_template("about.html")
    
    @app.route("/programes")
    def programes():
        return render_template("programes.html")
    
    @app.route("/contact")
    def contact():
        return render_template("contact.html")
    
    @app.route("/news")
    def news():
        return render_template("news.html")
    
    @app.route("/announcement")
    def announcement():
        return render_template("announcement.html")
    
    @app.route("/video")
    def video():
        return render_template("video.html")
    
    @app.route("/information")
    def information():
        return render_template("information.html")
    
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            middle_name = request.form.get("middle_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            
            # Validation
            if not all([first_name, last_name, email, phone, password, confirm_password]):
                flash("All required fields must be filled", "error")
                return render_template("signup.html")
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Please enter a valid email address", "error")
                return render_template("signup.html")
            
            if len(password) < 6:
                flash("Password must be at least 6 characters long", "error")
                return render_template("signup.html")
            
            if password != confirm_password:
                flash("Passwords do not match", "error")
                return render_template("signup.html")
            
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                flash("Email already registered. Please use a different email or login.", "error")
                return render_template("signup.html")
            
            # Create new user
            try:
                user = User(
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    email=email,
                    phone=phone
                )
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                flash("Account created successfully! Please login.", "success")
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                flash("An error occurred while creating your account. Please try again.", "error")
                return render_template("signup.html")
        
        return render_template("signup.html")
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
            
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            place = request.form.get("place", "").strip()
            password = request.form.get("password", "")
            
            # Validation
            if not email or not password or not place:
                flash("Please enter email, place, and password", "error")
                return render_template("login.html")
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash("Please enter a valid email address", "error")
                return render_template("login.html")
            
            # Check user credentials
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                if user.is_active:
                    login_user(user, remember=True)
                    next_page = request.args.get('next')
                    if not next_page or not next_page.startswith('/'):
                        next_page = url_for('home')
                    flash(f"Welcome back, {user.get_full_name()}! Logged in from {place}.", "success")
                    return redirect(next_page)
                else:
                    flash("Your account has been deactivated. Please contact support.", "error")
            else:
                flash("Invalid email or password", "error")
        
        return render_template("login.html")
    
    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out successfully.", "success")
        return redirect(url_for('home'))
    
    @app.route("/profile")
    @login_required
    def profile():
        return render_template("profile.html", user=current_user)
    
    @app.route("/application", methods=["GET", "POST"])
    @login_required
    def application():
        # Check if user has a pending application that needs payment
        pending_application = Application.query.filter_by(
            user_id=current_user.id, 
            status='pending',
            payment_completed=False
        ).first()
        
        if pending_application:
            flash("You have a pending application that requires payment. Please complete the payment first.", "warning")
            return redirect(url_for('payment_page', app_id=pending_application.id))
        if request.method == "POST":
            # Handle form submission
            try:
                # Get student information
                first_name = request.form.get("first_name", "").strip()
                second_name = request.form.get("second_name", "").strip()
                surname = request.form.get("surname", "").strip()
                nationality = request.form.get("nationality", "").strip()
                gender = request.form.get("gender", "").strip()
                religion = request.form.get("religion", "").strip()
                date_of_birth_str = request.form.get("date_of_birth", "").strip()
                place_of_birth = request.form.get("place_of_birth", "").strip()
                
                # Get father's information
                father_first_name = request.form.get("father_first_name", "").strip()
                father_second_name = request.form.get("father_second_name", "").strip()
                father_last_name = request.form.get("father_last_name", "").strip()
                father_occupation = request.form.get("father_occupation", "").strip()
                father_nida = request.form.get("father_nida", "").strip()
                father_telephone = request.form.get("father_telephone", "").strip()
                father_address = request.form.get("father_address", "").strip()
                father_street = request.form.get("father_street", "").strip()
                
                # Get mother's information
                mother_first_name = request.form.get("mother_first_name", "").strip()
                mother_second_name = request.form.get("mother_second_name", "").strip()
                mother_last_name = request.form.get("mother_last_name", "").strip()
                mother_occupation = request.form.get("mother_occupation", "").strip()
                mother_nida = request.form.get("mother_nida", "").strip()
                mother_telephone = request.form.get("mother_telephone", "").strip()
                mother_address = request.form.get("mother_address", "").strip()
                mother_street = request.form.get("mother_street", "").strip()
                
                # Get guardian's information (optional)
                guardian_first_name = request.form.get("guardian_first_name", "").strip()
                guardian_last_name = request.form.get("guardian_last_name", "").strip()
                guardian_occupation = request.form.get("guardian_occupation", "").strip()
                guardian_telephone = request.form.get("guardian_telephone", "").strip()
                guardian_address = request.form.get("guardian_address", "").strip()
                
                # Basic validation for required fields
                required_fields = [
                    first_name, surname, nationality, gender, date_of_birth_str, place_of_birth,
                    father_first_name, father_last_name, father_occupation, father_telephone, father_address,
                    mother_first_name, mother_last_name, mother_occupation, mother_telephone, mother_address
                ]
                
                if not all(required_fields):
                    flash("Please fill in all required fields marked with *", "error")
                    return render_template("application.html")
                
                # Convert date string to date object
                try:
                    date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
                except ValueError:
                    flash("Please enter a valid date of birth", "error")
                    return render_template("application.html")
                
                # Handle file uploads (optional)
                father_photo_path = None
                mother_photo_path = None
                guardian_photo_path = None
                
                # Save uploaded files if provided
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                
                for photo_field, photo_name in [
                    ('father_photo', 'father'),
                    ('mother_photo', 'mother'),
                    ('guardian_photo', 'guardian')
                ]:
                    photo_file = request.files.get(photo_field)
                    if photo_file and photo_file.filename:
                        # Generate unique filename
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{photo_name}_{timestamp}_{photo_file.filename}"
                        filepath = os.path.join(upload_folder, filename)
                        photo_file.save(filepath)
                        
                        # Store relative path
                        if photo_name == 'father':
                            father_photo_path = f"uploads/{filename}"
                        elif photo_name == 'mother':
                            mother_photo_path = f"uploads/{filename}"
                        elif photo_name == 'guardian':
                            guardian_photo_path = f"uploads/{filename}"
                
                # Create and save application to database
                application = Application(
                    # Student Information
                    first_name=first_name,
                    second_name=second_name,
                    surname=surname,
                    nationality=nationality,
                    gender=gender,
                    religion=religion,
                    date_of_birth=date_of_birth,
                    place_of_birth=place_of_birth,
                    
                    # Father's Information
                    father_first_name=father_first_name,
                    father_second_name=father_second_name,
                    father_last_name=father_last_name,
                    father_occupation=father_occupation,
                    father_nida=father_nida,
                    father_telephone=father_telephone,
                    father_address=father_address,
                    father_street=father_street,
                    father_photo=father_photo_path,
                    
                    # Mother's Information
                    mother_first_name=mother_first_name,
                    mother_second_name=mother_second_name,
                    mother_last_name=mother_last_name,
                    mother_occupation=mother_occupation,
                    mother_nida=mother_nida,
                    mother_telephone=mother_telephone,
                    mother_address=mother_address,
                    mother_street=mother_street,
                    mother_photo=mother_photo_path,
                    
                    # Guardian's Information
                    guardian_first_name=guardian_first_name or None,
                    guardian_last_name=guardian_last_name or None,
                    guardian_occupation=guardian_occupation or None,
                    guardian_telephone=guardian_telephone or None,
                    guardian_address=guardian_address or None,
                    guardian_photo=guardian_photo_path
                )
                
                # Set the user_id for the application
                application.user_id = current_user.id
                application.payment_required = True
                application.payment_completed = False
                
                db.session.add(application)
                db.session.commit()
                
                # Redirect to payment page
                flash("Application submitted successfully! Please complete the payment of Tsh 10,000/= to finalize your application.", "success")
                return redirect(url_for('payment_page', app_id=application.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while submitting your application: {str(e)}. Please try again.", "error")
                return render_template("application.html")
        
        # GET request - show the form
        return render_template("application.html")
    
    @app.route("/download/<path:filename>")
    def download_image(filename: str):
        images_dir = os.path.join(app.root_path, "static", "images")
        file_path = os.path.join(images_dir, filename)
        if not os.path.isfile(file_path):
            return abort(404)
        return send_from_directory(images_dir, filename, as_attachment=True)
    
    # ==================== ADMIN ROUTES ====================
    
    # Admin login
    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if request.method == "POST":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            
            admin = Admin.query.filter_by(email=email, is_active=True).first()
            
            if admin and admin.check_password(password):
                login_user(admin)
                admin.last_login = datetime.utcnow()
                db.session.commit()
                flash(f"Welcome back, {admin.full_name}!", "success")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid email or password", "error")
        
        return render_template("admin/login.html")
    
    # Admin dashboard
    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        # Get statistics
        total_applications = Application.query.count()
        pending_applications = Application.query.filter_by(status='pending').count()
        approved_applications = Application.query.filter_by(status='approved').count()
        total_payments = Payment.query.filter_by(status='completed').count()
        total_revenue = sum(payment.amount for payment in Payment.query.filter_by(status='completed').all())
        
        # Recent applications
        recent_applications = Application.query.order_by(Application.submitted_at.desc()).limit(5).all()
        
        return render_template("admin/dashboard.html", 
                             total_applications=total_applications,
                             pending_applications=pending_applications,
                             approved_applications=approved_applications,
                             total_payments=total_payments,
                             total_revenue=total_revenue,
                             recent_applications=recent_applications)
    
    # View all applications
    @app.route("/admin/applications")
    @login_required
    def admin_applications():
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        if not current_user.has_permission('view_applications'):
            flash("You don't have permission to view applications.", "error")
            return redirect(url_for('admin_dashboard'))
        
        applications = Application.query.order_by(Application.submitted_at.desc()).all()
        return render_template("admin/applications.html", applications=applications)
    
    # View single application
    @app.route("/admin/application/<int:app_id>")
    @login_required
    def admin_view_application(app_id):
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        application = Application.query.get_or_404(app_id)
        return render_template("admin/view_application.html", application=application)
    
    # Approve/Reject application
    @app.route("/admin/application/<int:app_id>/<action>")
    @login_required
    def admin_application_action(app_id, action):
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        if action not in ['approve', 'reject']:
            flash("Invalid action.", "error")
            return redirect(url_for('admin_applications'))
        
        if action == 'approve' and not current_user.has_permission('approve_applications'):
            flash("You don't have permission to approve applications.", "error")
            return redirect(url_for('admin_applications'))
        
        if action == 'reject' and not current_user.has_permission('reject_applications'):
            flash("You don't have permission to reject applications.", "error")
            return redirect(url_for('admin_applications'))
        
        application = Application.query.get_or_404(app_id)
        application.status = 'approved' if action == 'approve' else 'rejected'
        application.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        action_text = "approved" if action == 'approve' else "rejected"
        flash(f"Application for {application.get_student_name()} has been {action_text}.", "success")
        return redirect(url_for('admin_applications'))
    
    # View payments
    @app.route("/admin/payments")
    @login_required
    def admin_payments():
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        if not current_user.has_permission('view_payments'):
            flash("You don't have permission to view payments.", "error")
            return redirect(url_for('admin_dashboard'))
        
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        return render_template("admin/payments.html", payments=payments)
    
    # Manage payment status
    @app.route("/admin/payment/<int:payment_id>/<action>")
    @login_required
    def admin_payment_action(payment_id, action):
        if not isinstance(current_user, Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        if not current_user.has_permission('manage_payments'):
            flash("You don't have permission to manage payments.", "error")
            return redirect(url_for('admin_payments'))
        
        payment = Payment.query.get_or_404(payment_id)
        
        if action == 'complete':
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            payment.application.payment_completed = True
        elif action == 'refund':
            payment.status = 'refunded'
        elif action == 'fail':
            payment.status = 'failed'
        
        db.session.commit()
        
        flash(f"Payment {payment.transaction_id} has been {action}ed.", "success")
        return redirect(url_for('admin_payments'))
    
    # Admin logout
    @app.route("/admin/logout")
    @login_required
    def admin_logout():
        if isinstance(current_user, Admin):
            logout_user()
            flash("You have been logged out successfully.", "success")
        return redirect(url_for('home'))
    
    # ==================== PAYMENT ROUTES ====================
    
    # Payment page
    @app.route("/payment/<int:app_id>")
    @login_required
    def payment_page(app_id):
        application = Application.query.get_or_404(app_id)
        
        if application.user_id != current_user.id:
            flash("You can only pay for your own applications.", "error")
            return redirect(url_for('home'))
        
        if application.has_paid():
            flash("Payment already completed for this application.", "info")
            return redirect(url_for('home'))
        
        return render_template("payment.html", application=application)
    
    # Process payment
    @app.route("/payment/<int:app_id>/process", methods=["POST"])
    @login_required
    def process_payment(app_id):
        application = Application.query.get_or_404(app_id)
        
        if application.user_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        if application.has_paid():
            return jsonify({"success": False, "message": "Payment already completed"}), 400
        
        payment_method = request.form.get("payment_method")
        phone_number = request.form.get("phone_number")
        
        if not payment_method or not phone_number:
            return jsonify({"success": False, "message": "Missing required fields"}), 400
        
        # Create payment record
        payment = Payment(
            application_id=application.id,
            user_id=current_user.id,
            amount=10000.00,  # Tsh 10,000
            payment_method=payment_method,
            transaction_id=f"TXN_{uuid.uuid4().hex[:8].upper()}",
            phone_number=phone_number,
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # In a real application, you would integrate with payment gateway here
        # For now, we'll simulate a successful payment
        payment.status = 'completed'
        payment.completed_at = datetime.utcnow()
        application.payment_completed = True
        
        db.session.commit()
        
        flash("Payment completed successfully! Your application has been submitted.", "success")
        return jsonify({"success": True, "message": "Payment completed successfully"})
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)