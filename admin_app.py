from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import secrets
import sys

db = SQLAlchemy()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def create_admin_app():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.abspath(os.path.join(base_dir, '..'))
    template_dir = os.path.join(instance_path, 'templates')
    static_dir = os.path.join(instance_path, 'public')
    app = Flask(__name__, static_folder=static_dir, static_url_path='', template_folder=template_dir, instance_path=instance_path)

    app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    db_path = os.path.join(instance_path, 'library_db.sqlite3')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', secrets.token_hex(32))

    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

    db.init_app(app)
    jwt = JWTManager(app)

    # Import models here to register with SQLAlchemy
    from src.models import User, Book, BorrowRecord, Fees

    # Import and register only admin-related blueprints
    from src.features.admin_login import api_flask as admin_login_bp
    from src.features.dashboard.api import dashboard_bp
    from src.features.manage_users.api import manage_users_bp
    from src.features.book_management.api import book_management_bp
    from src.features.automated_fine_calculation.api import automated_fine_calculation_bp
    from src.features.due_date_fine_tracking.api import due_date_fine_tracking_bp
    from src.features.history.api import history_bp
    from src.features.dataset_management.api import dataset_management_bp

    app.register_blueprint(admin_login_bp.admin_login_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(manage_users_bp)
    app.register_blueprint(book_management_bp)
    app.register_blueprint(automated_fine_calculation_bp)
    app.register_blueprint(due_date_fine_tracking_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(dataset_management_bp)

    # Initialize and start the scheduler for automated fine calculation
    from src.features.automated_fine_calculation.scheduler import start_scheduler
    start_scheduler(app)

    return app

if __name__ == '__main__':
    app = create_admin_app()
    app.run(debug=True)
