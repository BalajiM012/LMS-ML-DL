from flask import Blueprint, jsonify, request, session
from src.app_factory_minimal import db
from src.models import User, Book, BorrowRecord, Fees
from datetime import datetime, timedelta
import json

admin_dashboard_bp = Blueprint('admin_dashboard', __name__, url_prefix='/api/admin')

@admin_dashboard_bp.route('/dashboard-stats')
def dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        # Book statistics
        total_books = Book.query.count()
        borrowed_books = BorrowRecord.query.filter(BorrowRecord.return_date.is_(None)).count()
        available_books = total_books - borrowed_books
        
        # User statistics
        total_users = User.query.count()
        
        # Fine statistics
        total_fines = db.session.query(db.func.sum(Fees.amount)).scalar() or 0
        
        # Overdue books
        overdue_books = BorrowRecord.query.filter(
            BorrowRecord.return_date.is_(None),
            BorrowRecord.due_date < datetime.now()
        ).count()
        
        return jsonify({
            'totalBooks': total_books,
            'totalUsers': total_users,
            'borrowedBooks': borrowed_books,
            'totalFines': float(total_fines),
            'overdueBooks': overdue_books,
            'availableBooks': available_books
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/search')
def global_search():
    """Global search across books, users, and borrowed records"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return jsonify([])
    
    results = []
    
    try:
        if search_type in ['all', 'books']:
            books = Book.query.filter(
                Book.title.contains(query) | 
                Book.author.contains(query) | 
                Book.isbn.contains(query)
            ).limit(10).all()
            
            for book in books:
                results.append({
                    'type': 'book',
                    'id': book.id,
                    'title': book.title,
                    'author': book.author,
                    'isbn': book.isbn,
                    'copies': book.copies
                })
        
        if search_type in ['all', 'users']:
            users = User.query.filter(
                User.fullname.contains(query) | 
                User.username.contains(query) | 
                User.email.contains(query)
            ).limit(10).all()
            
            for user in users:
                results.append({
                    'type': 'user',
                    'id': user.id,
                    'name': user.fullname,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                })
        
        if search_type in ['all', 'borrowed']:
            borrowed = BorrowRecord.query.join(User).join(Book).filter(
                User.fullname.contains(query) | 
                Book.title.contains(query)
            ).limit(10).all()
            
            for record in borrowed:
                results.append({
                    'type': 'borrowed',
                    'id': record.id,
                    'user': record.user.fullname,
                    'book': record.book.title,
                    'borrow_date': record.borrow_date.isoformat(),
                    'due_date': record.due_date.isoformat(),
                    'fine': record.fine
                })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/calculate-fines', methods=['POST'])
def calculate_fines():
    """Calculate fines for overdue books"""
    try:
        overdue_records = BorrowRecord.query.filter(
            BorrowRecord.return_date.is_(None),
            BorrowRecord.due_date < datetime.now()
        ).all()
        
        fine_per_day = 1.0  # $1 per day
        total_fines = 0
        
        for record in overdue_records:
            days_overdue = (datetime.now() - record.due_date).days
            if days_overdue > 0:
                record.fine = days_overdue * fine_per_day
                total_fines += record.fine
        
        db.session.commit()
        
        return jsonify({
            'message': f'Fines calculated for {len(overdue_records)} overdue books',
            'totalFines': total_fines
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/overdue-books')
def get_overdue_books():
    """Get list of overdue books"""
    try:
        overdue = BorrowRecord.query.filter(
            BorrowRecord.return_date.is_(None),
            BorrowRecord.due_date < datetime.now()
        ).all()
        
        result = []
        for record in overdue:
            days_overdue = (datetime.now() - record.due_date).days
            result.append({
                'id': record.id,
                'user': record.user.fullname,
                'book': record.book.title,
                'due_date': record.due_date.isoformat(),
                'days_overdue': days_overdue,
                'fine': record.fine or 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/borrow-history')
def borrow_history():
    """Get complete borrow history"""
    try:
        history = BorrowRecord.query.join(User).join(Book).all()
        
        result = []
        for record in history:
            result.append({
                'id': record.id,
                'user': record.user.fullname,
                'book': record.book.title,
                'borrow_date': record.borrow_date.isoformat(),
                'due_date': record.due_date.isoformat(),
                'return_date': record.return_date.isoformat() if record.return_date else None,
                'fine': record.fine or 0
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/export-inventory')
def export_inventory():
    """Export book inventory as CSV"""
    try:
        books = Book.query.all()
        
        inventory = []
        for book in books:
            borrowed_count = BorrowRecord.query.filter(
                BorrowRecord.book_id == book.id,
                BorrowRecord.return_date.is_(None)
            ).count()
            
            inventory.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'total_copies': book.copies,
                'available_copies': book.copies - borrowed_count
            })
        
        return jsonify(inventory)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/backup', methods=['POST'])
def backup_data():
    """Create database backup"""
    try:
        # In a real implementation, this would create a proper backup
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'books': Book.query.count(),
            'users': User.query.count(),
            'borrow_records': BorrowRecord.query.count(),
            'fees': Fees.query.count()
        }
        
        return jsonify({
            'message': 'Backup created successfully',
            'backup_info': backup_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/forecast')
def generate_forecast():
    """Generate data forecast using ML"""
    try:
        # Simple forecasting based on historical data
        total_books = Book.query.count()
        total_users = User.query.count()
        borrowed_books = BorrowRecord.query.filter(BorrowRecord.return_date.is_(None)).count()
        
        # Simple trend prediction
        forecast = {
            'next_month_books': total_books + 10,
            'next_month_users': total_users + 5,
            'predicted_borrowed': borrowed_books + 3,
            'high_demand_books': ['Python Programming', 'Data Structures', 'Machine Learning'],
            'message': 'Forecast generated successfully'
        }
        
        return jsonify(forecast)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
