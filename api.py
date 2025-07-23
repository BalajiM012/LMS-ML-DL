from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from src.app_factory import db
from src.models import User

admin_login_bp = Blueprint('admin_login', __name__, url_prefix='/admin')

from flask import render_template, request, redirect, url_for, session
from src.app_factory import db
from src.models import User

@admin_login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Authentication logic here (simplified for example)
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:  # Simplified, replace with hash check
            session['user_id'] = user.id
            session['role'] = 'admin'
            return redirect(url_for('home_ui.admin'))
        else:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@admin_login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login.login'))

@admin_login_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    return render_template('admin_dashboard.html')
