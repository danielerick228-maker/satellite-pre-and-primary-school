from flask import Flask, render_template, send_from_directory, abort, request, redirect, url_for, flash, jsonify, current_app
try:
    from flask_talisman import Talisman
except Exception:
    Talisman = None
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
import re
import uuid
from datetime import datetime
from config import Config
from models import db, User, Application, Admin, Payment
from database import init_db, init_migrations
from werkzeug.utils import secure_filename

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Security headers via Talisman (if available)
    if Talisman is not None:
        csp = {
            'default-src': ["'self'"],
            'img-src': ["'self'", 'data:'],
            'style-src': ["'self'", "'unsafe-inline'"],
            'script-src': ["'self'", "'unsafe-inline'"]
        }
        Talisman(
            app,
            content_security_policy=csp,
            force_https=bool(int(os.environ.get('FORCE_HTTPS', '0'))),
            frame_options='DENY',
            strict_transport_security=True,
            session_cookie_secure=app.config.get('SESSION_COOKIE_SECURE', False)
        )
    
    # Initialize database and migrations
    init_db(app)
    init_migrations(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.unauthorized_handler
    def handle_unauthorized():
        next_url = request.url
        try:
            if request.path.startswith('/admin'):
                return redirect(url_for('admin_login', next=next_url))
        except Exception:
            pass
        return redirect(url_for('login', next=next_url))
    
    @login_manager.user_loader
    def load_user(user_id: str):
        # Support both user and admin IDs with type prefix
        try:
            if not user_id:
                return None
            if user_id.startswith('admin:'):
                admin_id = int(user_id.split(':', 1)[1])
                return Admin.query.get(admin_id)
            if user_id.startswith('user:'):
                uid = int(user_id.split(':', 1)[1])
                return User.query.get(uid)
            # Backward compatibility: numeric IDs treated as User
            return User.query.get(int(user_id))
        except Exception:
            return None

    # =============== SIMPLE CONTENT STORAGE (JSON) ===============
    import json
    def _content_path():
        data_dir = os.path.join(app.root_path, 'instance')
        os.makedirs(data_dir, exist_ok=True)
        return os.path.join(data_dir, 'site_content.json')

    def get_site_content():
        try:
            with open(_content_path(), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "announcement_title": None,
                "announcement_subtitle": None,
                "announcement_message": None,
                "information_html": None
            }

    def save_site_content(payload: dict):
        content = get_site_content()
        content.update({k: v for k, v in payload.items() if k in content})
        with open(_content_path(), 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    
    # Your existing routes
    @app.route("/")
    def home():
        return render_template("announcement.html", site_content=get_site_content())
    
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
        return render_template("announcement.html", site_content=get_site_content())
    
    @app.route("/video")
    def video():
        return render_template("video.html")
    
    @app.route("/information")
    def information():
        return render_template("information.html", site_content=get_site_content())
    
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

            # Allow admin to log in from the same form using configured credentials
            allowed_admin_email = current_app.config.get('ADMIN_LOGIN_EMAIL')
            allowed_admin_password = current_app.config.get('ADMIN_LOGIN_PASSWORD')
            if allowed_admin_email and email.lower() == allowed_admin_email.lower():
                admin = Admin.query.filter_by(email=email).first()
                if not admin:
                    # Create admin only if the provided password matches configured one
                    if allowed_admin_password and password == allowed_admin_password:
                        admin = Admin(
                            email=email,
                            full_name='System Administrator',
                            role='super_admin',
                            permissions=None,
                            is_active=True
                        )
                        admin.set_password(password)
                        db.session.add(admin)
                        db.session.commit()
                    else:
                        flash("Invalid email or password", "error")
                        return render_template("login.html")
                # Verify password and log in admin
                if admin.check_password(password):
                    login_user(admin, remember=True)
                    admin.last_login = datetime.utcnow()
                    db.session.commit()
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid email or password", "error")
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
            
            # Only allow configured admin email
            allowed_email = app.config.get('ADMIN_LOGIN_EMAIL')
            allowed_password = app.config.get('ADMIN_LOGIN_PASSWORD')
            if email.lower() != allowed_email.lower():
                flash("Access denied. This email is not authorized for admin login.", "error")
                return render_template("admin/login.html")
 
            admin = Admin.query.filter_by(email=email, is_active=True).first()
            
            # Auto-create admin if not exists and correct configured password provided
            if not admin:
                if password != allowed_password:
                    flash("Invalid email or password", "error")
                    return render_template("admin/login.html")
                admin = Admin(
                    email=email,
                    full_name='System Administrator',
                    role='super_admin',
                    permissions=None,
                    is_active=True
                )
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
            
            # Validate password
            if admin.check_password(password):
                login_user(admin)
                admin.last_login = datetime.utcnow()
                db.session.commit()
                flash(f"Welcome back, {admin.full_name}!", "success")
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/admin'):
                    next_page = url_for('admin_dashboard')
                return redirect(next_page)
            else:
                flash("Invalid email or password", "error")
        
        return render_template("admin/login.html")
    
    # Admin dashboard
    @app.route("/admin/dashboard")
    @login_required
    def admin_dashboard():
        # Ensure only Admin model can access
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        # Get statistics
        total_applications = Application.query.count()
        pending_applications = Application.query.filter_by(status='pending').count()
        approved_applications = Application.query.filter_by(status='approved').count()
        completed_payments = Payment.query.filter_by(status='completed').all()
        total_payments = len(completed_payments)
        total_revenue = sum(float(p.amount) for p in completed_payments)

        # Category revenue (heuristic by matching configured amounts)
        def amounts_from_config(key: str):
            cfg = current_app.config.get(key, [])
            try:
                return {float(item.get('amount', 0)) for item in cfg}
            except Exception:
                return set()

        fees_amounts = amounts_from_config('FEES_LIPA_NAMBAS')
        meals_amounts = amounts_from_config('MEALS_LIPA_NAMBAS')
        transport_amounts = amounts_from_config('TRANSPORT_LIPA_NAMBAS')

        fees_revenue = sum(float(p.amount) for p in completed_payments if float(p.amount) in fees_amounts)
        meals_revenue = sum(float(p.amount) for p in completed_payments if float(p.amount) in meals_amounts)
        transport_revenue = sum(float(p.amount) for p in completed_payments if float(p.amount) in transport_amounts)
        
        # Recent applications
        recent_applications = Application.query.order_by(Application.submitted_at.desc()).limit(5).all()
        
        return render_template("admin/dashboard.html", 
                             total_applications=total_applications,
                             pending_applications=pending_applications,
                             approved_applications=approved_applications,
                             total_payments=total_payments,
                             total_revenue=total_revenue,
                             fees_revenue=fees_revenue,
                             meals_revenue=meals_revenue,
                             transport_revenue=transport_revenue,
                             recent_applications=recent_applications)

    # ==================== ADMIN RESULTS UPLOAD ====================
    @app.route('/admin/results', methods=['GET', 'POST'])
    @login_required
    def admin_results():
        # Ensure only Admin model can access
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))

        results_dir = os.path.join(app.root_path, 'static', 'results')
        os.makedirs(results_dir, exist_ok=True)

        if request.method == 'POST':
            file = request.files.get('file')
            if not file or not file.filename:
                flash('Please choose a file to upload.', 'error')
                return redirect(url_for('admin_results'))
            filename = secure_filename(file.filename)
            if not filename:
                flash('Invalid file name.', 'error')
                return redirect(url_for('admin_results'))
            try:
                file.save(os.path.join(results_dir, filename))
                flash('Results file uploaded successfully.', 'success')
            except Exception as e:
                flash(f'Upload failed: {str(e)}', 'error')
            return redirect(url_for('admin_results'))

        # List existing result files
        files = []
        try:
            for name in sorted(os.listdir(results_dir)):
                path = os.path.join(results_dir, name)
                if os.path.isfile(path):
                    files.append({
                        'name': name,
                        'size': os.path.getsize(path)
                    })
        except Exception:
            pass

        return render_template('admin/results.html', files=files)

    @app.route('/results/<path:filename>')
    def public_results(filename: str):
        results_dir = os.path.join(app.root_path, 'static', 'results')
        file_path = os.path.join(results_dir, filename)
        if not os.path.isfile(file_path):
            return abort(404)
        return send_from_directory(results_dir, filename, as_attachment=True)

    @app.route('/results-list')
    def results_list():
        results_dir = os.path.join(app.root_path, 'static', 'results')
        files = []
        try:
            os.makedirs(results_dir, exist_ok=True)
            for name in sorted(os.listdir(results_dir)):
                path = os.path.join(results_dir, name)
                if os.path.isfile(path):
                    files.append({
                        'name': name,
                        'size': os.path.getsize(path)
                    })
        except Exception:
            pass
        return render_template('results_list.html', files=files)

    # =============== ADMIN CONTENT MANAGEMENT ===============
    @app.route('/admin/content', methods=['GET', 'POST'])
    @login_required
    def admin_content():
        # Ensure only Admin model can access
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        if request.method == 'POST':
            title = request.form.get('announcement_title', '').strip() or None
            subtitle = request.form.get('announcement_subtitle', '').strip() or None
            message = request.form.get('announcement_message', '').strip() or None
            info_html = request.form.get('information_html', '').strip() or None
            try:
                save_site_content({
                    'announcement_title': title,
                    'announcement_subtitle': subtitle,
                    'announcement_message': message,
                    'information_html': info_html
                })
                flash('Site content updated successfully.', 'success')
            except Exception as e:
                flash(f'Failed to update content: {str(e)}', 'error')
        return render_template('admin/content.html', site_content=get_site_content())
    
    # View all applications
    @app.route("/admin/applications")
    @login_required
    def admin_applications():
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
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
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        application = Application.query.get_or_404(app_id)
        return render_template("admin/view_application.html", application=application)
    
    # Approve/Reject application
    @app.route("/admin/application/<int:app_id>/<action>")
    @login_required
    def admin_application_action(app_id, action):
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
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
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        
        if not current_user.has_permission('view_payments'):
            flash("You don't have permission to view payments.", "error")
            return redirect(url_for('admin_dashboard'))
        
        raw_payments = Payment.query.order_by(Payment.payment_date.desc()).all()

        # Build category mapping by configured amounts (lightweight approach without schema change)
        def amounts_from_config(key: str):
            cfg = current_app.config.get(key, [])
            try:
                return {float(item.get('amount', 0)) for item in cfg}
            except Exception:
                return set()

        fees_amounts = amounts_from_config('FEES_LIPA_NAMBAS')
        meals_amounts = amounts_from_config('MEALS_LIPA_NAMBAS')
        transport_amounts = amounts_from_config('TRANSPORT_LIPA_NAMBAS')
        application_amounts = {float(current_app.config.get('APPLICATION_FEE_AMOUNT', 10000))}

        def categorize_payment(p: Payment) -> str:
            amt = float(p.amount)
            if amt in fees_amounts:
                return 'fees'
            if amt in meals_amounts:
                return 'meals'
            if amt in transport_amounts:
                return 'transport'
            if amt in application_amounts:
                return 'application'
            return 'unknown'

        # Prepare view models
        payments = [{
            'id': p.id,
            'transaction_id': p.transaction_id,
            'application_id': p.application_id,
            'application': p.application,
            'user': p.user,
            'amount': float(p.amount),
            'payment_method': p.payment_method,
            'phone_number': p.phone_number,
            'status': p.status,
            'payment_date': p.payment_date,
            'category': categorize_payment(p)
        } for p in raw_payments]

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
        # Allow logout only if current principal is admin
        if hasattr(current_user, 'role') and isinstance(current_user._get_current_object(), Admin):
            logout_user()
            flash("You have been logged out successfully.", "success")
            return redirect(url_for('home'))
        flash("Access denied.", "error")
        return redirect(url_for('home'))

    # ==================== ADMIN USERS MANAGEMENT ====================
    @app.route("/admin/users")
    @login_required
    def admin_users():
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        if not current_user.has_permission('manage_users') and current_user.role != 'super_admin':
            flash("You don't have permission to manage users.", "error")
            return redirect(url_for('admin_dashboard'))
        users = User.query.order_by(User.created_at.desc()).all()
        return render_template("admin/users.html", users=users)

    @app.route("/admin/users/purge", methods=["POST"])
    @login_required
    def admin_users_purge():
        if not hasattr(current_user, 'role') or not isinstance(current_user._get_current_object(), Admin):
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for('home'))
        if current_user.role != 'super_admin':
            flash("Only super admins can purge users.", "error")
            return redirect(url_for('admin_users'))
        try:
            # Delete payments and applications for non-admin users, then delete the users
            non_admin_users = User.query.all()
            app_ids = [a.id for a in Application.query.filter(Application.user_id.in_([u.id for u in non_admin_users])).all()]
            # Delete payments first (FK to application)
            Payment.query.filter(Payment.application_id.in_(app_ids)).delete(synchronize_session=False)
            # Delete applications
            Application.query.filter(Application.id.in_(app_ids)).delete(synchronize_session=False)
            # Delete users
            User.query.delete()
            db.session.commit()
            flash("All registered users and their applications/payments have been purged.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Purge failed: {str(e)}", "error")
        return redirect(url_for('admin_users'))
    
    # ==================== PAYMENT ROUTES ====================
    
    # Single-entry payment page for submission fee
    @app.route("/payment")
    @login_required
    def payment_entry():
        # Find the most recent pending application requiring payment
        pending = (
            Application.query
            .filter_by(user_id=current_user.id, status='pending', payment_completed=False)
            .order_by(Application.submitted_at.desc())
            .first()
        )
        if pending:
            return redirect(url_for('payment_page', app_id=pending.id))
        flash("No pending application payment found.", "info")
        return redirect(url_for('application'))

    # Category payment pages
    @app.route("/payments/fees")
    @login_required
    def payments_fees():
        tills = current_app.config.get('FEES_LIPA_NAMBAS', [])
        return render_template("payments/fees.html", tills=tills)

    @app.route("/payments/meals")
    @login_required
    def payments_meals():
        tills = current_app.config.get('MEALS_LIPA_NAMBAS', [])
        return render_template("payments/meals.html", tills=tills)

    @app.route("/payments/transport")
    @login_required
    def payments_transport():
        tills = current_app.config.get('TRANSPORT_LIPA_NAMBAS', [])
        return render_template("payments/transport.html", tills=tills)
    
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
        
        # Try to find an existing control number (stored in transaction_id starting with 'CN')
        existing_cn = (
            Payment.query
            .filter(
                Payment.application_id == app_id,
                Payment.user_id == current_user.id,
                Payment.transaction_id.like('CN%')
            )
            .order_by(Payment.payment_date.desc())
            .first()
        )
        control_number = existing_cn.transaction_id if existing_cn else None
        
        app_lipas = current_app.config.get('APPLICATION_LIPA_NAMBAS')
        if app_lipas and len(app_lipas) > 0:
            lipa_namba = app_lipas[0]
        else:
            lipa_namba = {
                "till": current_app.config.get('LIPA_NAMBA_TILL'),
                "name": current_app.config.get('LIPA_NAMBA_NAME'),
                "amount": current_app.config.get('APPLICATION_FEE_AMOUNT', 10000)
            }

        # Include primary tills for clarity on the payment page
        fees_list = current_app.config.get('FEES_LIPA_NAMBAS') or []
        meals_list = current_app.config.get('MEALS_LIPA_NAMBAS') or []
        transport_list = current_app.config.get('TRANSPORT_LIPA_NAMBAS') or []
        fees_primary = fees_list[0] if len(fees_list) > 0 else None
        meals_primary = meals_list[0] if len(meals_list) > 0 else None
        transport_primary = transport_list[0] if len(transport_list) > 0 else None

        return render_template(
            "payment.html",
            application=application,
            control_number=control_number,
            lipa_namba=lipa_namba,
            fees_till=fees_primary,
            meals_till=meals_primary,
            transport_till=transport_primary
        )
    
    # Process payment
    @app.route("/payment/<int:app_id>/process", methods=["POST"])
    @login_required
    def process_payment(app_id):
        application = Application.query.get_or_404(app_id)
        
        if application.user_id != current_user.id:
            return jsonify({"success": False, "message": "Unauthorized"}), 403
        
        if application.has_paid():
            return jsonify({"success": False, "message": "Payment already completed"}), 400
        
        # For control number flow, this endpoint no longer charges.
        # Keep it for backward compatibility – return guidance.
        return jsonify({
            "success": False,
            "message": "Use 'Generate Control Number' to get your reference number and pay via approved channels."
        }), 400

    @app.route("/payment/<int:app_id>/generate-control", methods=["POST"])
    @login_required
    def generate_control_number(app_id):
        # Endpoint deprecated in favor of LIPA NAMBA; return 410 Gone
        return jsonify({
            "success": False,
            "message": "This endpoint is deprecated. Use LIPA NAMBA instructions on the payment page."
        }), 410
    
    # Ensure a default admin exists using configured credentials
    try:
        with app.app_context():
            seed_email = app.config.get('ADMIN_LOGIN_EMAIL') or Config.ADMIN_LOGIN_EMAIL
            seed_password = app.config.get('ADMIN_LOGIN_PASSWORD') or getattr(Config, 'ADMIN_LOGIN_PASSWORD', None)
            if seed_email and seed_password:
                existing_admin = Admin.query.filter_by(email=seed_email).first()
                if not existing_admin:
                    admin = Admin(
                        email=seed_email,
                        full_name='System Administrator',
                        role='super_admin',
                        permissions=None,
                        is_active=True
                    )
                    admin.set_password(seed_password)
                    db.session.add(admin)
                    db.session.commit()
    except Exception:
        pass

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)