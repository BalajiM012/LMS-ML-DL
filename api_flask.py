from flask import Blueprint, render_template, redirect, url_for, session

admin_login_bp = Blueprint('admin_login', __name__)

@admin_login_bp.route('/admin')
def admin_home():
    # Check if admin is logged in (simple example)
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login.login'))
    user = {'fullname': 'Admin User'}  # Example user info
    return render_template('admin.html', user=user)

@admin_login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login.login'))

@admin_login_bp.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login.login'))
    user_fullname = 'Admin'  # You can replace this with actual user info from session or DB
    return render_template('admin_dashboard.html', admin_base_url='/admin', user_fullname=user_fullname)

from flask import request

@admin_login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Simplified authentication check
        if username == 'admin' and password == 'password':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_login.admin_home'))
        else:
            error = 'Invalid credentials'
            return render_template('admin_login.html', error=error)
    else:
        return render_template('admin_login.html')
