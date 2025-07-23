from flask import Flask
from flask_sqlalchemy import SQLAlchemy
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
    
    # Enable CORS for all routes
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

    db.init_app(app)

    # Import models here to register with SQLAlchemy
    from src.models import User, Book, BorrowRecord, Fees

    # Import and register blueprints
    from src.features.auth.api import auth_bp
    from src.features.ml_api import ml_bp
    from src.features.student_api import student_bp
    from src.features.admin_api import admin_bp
    from src.features.admin_dashboard_api import admin_dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ml_bp, url_prefix='/api/ml_api')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(admin_dashboard_bp, url_prefix='/api/admin')

    # Serve static files
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
