from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import secrets

db = SQLAlchemy()

def create_app():
    import os
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.abspath(os.path.join(base_dir, '..'))
    template_dir = os.path.join(instance_path, 'templates')
    static_dir = os.path.join(instance_path, 'public')
    app = Flask(__name__, static_folder=static_dir, static_url_path='', template_folder=template_dir, instance_path=instance_path)
    
    # Generate secure secret keys
    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    db_path = os.path.join(instance_path, 'library_db.sqlite3')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

    db.init_app(app)
    jwt = JWTManager(app)

    # Import models here to register with SQLAlchemy
    from src.models import User, Book, BorrowRecord, Fees

    # Import and register blueprints
    from src.features.book_recommendation.api import book_recommendation_bp
    from src.features.book_management.api import book_management_bp
    from src.features.student_login.api import student_login_bp
    from src.features.user_login import api_flask as user_login_bp
    from src.features.admin_login import api as admin_login_module
    from src.features.auth.api import auth_bp

    from src.features.demand_forecast.api import demand_forecast_bp
    from src.features.due_date_fine_tracking.api import due_date_fine_tracking_bp
    from src.features.automated_fine_calculation.api import automated_fine_calculation_bp
    from src.features.home_ui.api import home_ui_bp
    from src.features.dashboard.api import dashboard_bp
    from src.features.student_portal.api import student_portal_bp
    from src.features.dataset_management.api import dataset_management_bp
    from src.features.history.api import history_bp
    from src.features.manage_users.api import manage_users_bp
    from src.features.student.api import student_bp
    from src.features.student_ui.api import student_ui_bp
    # from src.features.ml_api import ml_bp  # Temporarily disabled
    from src.api_routes import api_bp

    app.register_blueprint(book_recommendation_bp, url_prefix='/api/book_recommendation')
    app.register_blueprint(book_management_bp, url_prefix='/api/book_management')
    app.register_blueprint(student_login_bp, url_prefix='/api/student_login')
    app.register_blueprint(user_login_bp.user_login_bp, url_prefix='/api/user_login')
    app.register_blueprint(admin_login_module.admin_login_bp, url_prefix='/api/admin_login')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(demand_forecast_bp, url_prefix='/api/demand_forecast')
    app.register_blueprint(due_date_fine_tracking_bp, url_prefix='/api/due_date_fine_tracking')
    app.register_blueprint(automated_fine_calculation_bp, url_prefix='/api/automated_fine_calculation')
    app.register_blueprint(home_ui_bp, url_prefix='/api/home_ui')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(student_portal_bp, url_prefix='/api/student_portal')
    app.register_blueprint(dataset_management_bp, url_prefix='/api/dataset_management')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(manage_users_bp, url_prefix='/api/manage_users')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(student_ui_bp, url_prefix='/api/student_ui')
    # app.register_blueprint(ml_bp, url_prefix='/api/ml_api')  # Temporarily disabled

    # Initialize and start the scheduler for automated fine calculation
    from src.features.automated_fine_calculation.scheduler import start_scheduler
    start_scheduler(app)

    from flask import redirect

    @app.route('/api/admin_login/admin')
    def redirect_admin():
        return redirect('/api/admin_login/admin_home')

    # Serve main HTML pages for ML features
    @app.route('/ml_dashboard')
    def ml_dashboard():
        return app.send_static_file('ml_dashboard.html')

    @app.route('/ml_styles.css')
    def ml_styles():
        return app.send_static_file('ml_styles.css')

    return app
