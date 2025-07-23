from flask import Blueprint, jsonify, request, session
from src.models import db, User, Book, BorrowRecord, Fees
from datetime import datetime, timedelta
from sqlalchemy import func, and_

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
def get_admin_dashboard():
    """Get comprehensive admin dashboard data"""
    try:
        # Check if user is admin
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get dashboard statistics
        total_books = Book.query.count()
        total_users = User.query.count()
        borrowed_books = BorrowRecord.query.filter_by(return_date=None).count()
        total_fines = db.session.query(
            func.coalesce(func.sum(Fees.amount), 0)
        ).scalar()
        
        active_students = User.query.filter_by(role='student').count()
        overdue_books = BorrowRecord.query.filter(
            and_(
                BorrowRecord.return_date.is_(None),
                BorrowRecord.due_date < datetime.utcnow()
            )
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'totalBooks': total_books,
                'totalUsers': total_users,
                'borrowedBooks': borrowed_books,
                'totalFines': float(total_fines),
                'activeStudents': active_students,
                'overdueBooks': overdue_books
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/activity', methods=['GET'])
def get_admin_activity():
    """Get recent admin activity"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Get recent activities (last 20)
        activities = []
        
        # Recent book additions
        recent_books = Book.query.order_by(Book.id.desc()).limit(5).all()
        for book in recent_books:
            activities.append({
                'type': 'book_added',
                'title': 'Book Added',
                'description': f"New book '{book.title}' by {book.author} added",
                'date': datetime.utcnow().isoformat()
            })
        
        # Recent user registrations
        recent_users = User.query.order_by(User.id.desc()).limit(5).all()
        for user in recent_users:
            activities.append({
                'type': 'user_registered',
                'title': 'User Registered',
                'description': f"New {user.role} '{user.fullname}' registered",
                'date': datetime.utcnow().isoformat()
            })
        
        # Recent borrowings
        recent_borrows = BorrowRecord.query.order_by(BorrowRecord.borrow_date.desc()).limit(5).all()
        for record in recent_borrows:
            book = Book.query.get(record.book_id)
            user = User.query.get(record.user_id)
            activities.append({
                'type': 'book_borrowed',
                'title': 'Book Borrowed',
                'description': f"'{book.title}' borrowed by {user.fullname}",
                'date': record.borrow_date.isoformat()
            })
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/search', methods=['GET'])
def admin_search():
    """Admin search functionality"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'books')
        
        results = []
        
        if search_type == 'books':
            books = Book.query.filter(
                Book.title.ilike(f'%{query}%') |
                Book.author.ilike(f'%{query}%') |
                Book.isbn.ilike(f'%{query}%')
            ).limit(10).all()
            
            results = [{
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'category': book.category,
                'available_quantity': book.available_quantity,
                'total_quantity': book.total_quantity
            } for book in books]
        
        elif search_type == 'users':
            users = User.query.filter(
                User.fullname.ilike(f'%{query}%') |
                User.username.ilike(f'%{query}%') |
                User.email.ilike(f'%{query}%')
            ).limit(10).all()
            
            results = [{
                'id': user.id,
                'fullname': user.fullname,
                'username': user.username,
                'email': user.email,
                'role': user.role
            } for user in users]
        
        elif search_type == 'borrowed':
            records = BorrowRecord.query.join(User).join(Book).filter(
                User.fullname.ilike(f'%{query}%') |
                Book.title.ilike(f'%{query}%')
            ).limit(10).all()
            
            results = [{
                'id': record.id,
                'user_name': record.user.fullname,
                'book_title': record.book.title,
                'borrow_date': record.borrow_date.isoformat(),
                'due_date': record.due_date.isoformat(),
                'return_date': record.return_date.isoformat() if record.return_date else None
            } for record in records]
        
        elif search_type == 'fines':
            fines = Fees.query.join(User).filter(
                User.fullname.ilike(f'%{query}%') |
                Fees.reason.ilike(f'%{query}%')
            ).limit(10).all()
            
            results = [{
                'id': fine.id,
                'user_name': fine.user.fullname,
                'amount': float(fine.amount),
                'reason': fine.reason,
                'date': fine.date.isoformat()
            } for fine in fines]
        
        return jsonify({
            'success': True,
            'results': results,
            'type': search_type,
            'query': query
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/books', methods=['GET'])
def get_all_books():
    """Get all books with pagination"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        books = Book.query.paginate(page=page, per_page=per_page, error_out=False)
        
        books_data = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'category': book.category,
            'available_quantity': book.available_quantity,
            'total_quantity': book.total_quantity,
            'description': book.description
        } for book in books.items]
        
        return jsonify({
            'success': True,
            'books': books_data,
            'total': books.total,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/books', methods=['POST'])
def add_book():
    """Add a new book"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        book = Book(
            title=data['title'],
            author=data['author'],
            isbn=data['isbn'],
            category=data.get('category', ''),
            total_quantity=data['total_quantity'],
            available_quantity=data['total_quantity'],
            description=data.get('description', '')
        )
        
        db.session.add(book)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book added successfully',
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        book = Book.query.get_or_404(book_id)
        data = request.get_json()
        
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.isbn = data.get('isbn', book.isbn)
        book.category = data.get('category', book.category)
        book.description = data.get('description', book.description)
        
        if 'total_quantity' in data:
            book.total_quantity = data['total_quantity']
            book.available_quantity = data['total_quantity'] - (book.total_quantity - book.available_quantity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        book = Book.query.get_or_404(book_id)
        
        # Check if book has active borrow records
        active_borrows = BorrowRecord.query.filter_by(
            book_id=book_id,
            return_date=None
        ).count()
        
        if active_borrows > 0:
            return jsonify({'error': 'Cannot delete book with active borrows'}), 400
        
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """Get all users with pagination"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = [{
            'id': user.id,
            'fullname': user.fullname,
            'username': user.username,
            'email': user.email,
            'role': user.role
        } for user in users.items]
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': users.total,
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        admin_user = User.query.get(session['user_id'])
        if not admin_user or admin_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        user.fullname = data.get('fullname', user.fullname)
        user.email = data.get('email', user.email)
        user.role = data.get('role', user.role)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        admin_user = User.query.get(session['user_id'])
        if not admin_user or admin_user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Check if user has active borrow records
        active_borrows = BorrowRecord.query.filter_by(
            user_id=user_id,
            return_date=None
        ).count()
        
        if active_borrows > 0:
            return jsonify({'error': 'Cannot delete user with active borrows'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/borrowing-records', methods=['GET'])
def get_borrowing_records():
    """Get all borrowing records"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        records = BorrowRecord.query.join(User).join(Book).all()
        
        records_data = [{
            'id': record.id,
            'user_name': record.user.fullname,
            'book_title': record.book.title,
            'borrow_date': record.borrow_date.isoformat(),
            'due_date': record.due_date.isoformat(),
            'return_date': record.return_date.isoformat() if record.return_date else None,
            'fine': float(record.fine) if record.fine else 0
        } for record in records]
        
        return jsonify({
            'success': True,
            'records': records_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/fines', methods=['GET'])
def get_all_fines():
    """Get all fines"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        fines = Fees.query.join(User).all()
        
        fines_data = [{
            'id': fine.id,
            'user_name': fine.user.fullname,
            'amount': float(fine.amount),
            'reason': fine.reason,
            'date': fine.date.isoformat()
        } for fine in fines]
        
        return jsonify({
            'success': True,
            'fines': fines_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reports', methods=['GET'])
def generate_reports():
    """Generate admin reports"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Access denied'}), 403
        
        report_type = request.args.get('type', 'summary')
        
        if report_type == 'summary':
            # Summary report
            total_books = Book.query.count()
            total_users = User.query.count()
            borrowed_books = BorrowRecord.query.filter_by(return_date=None).count()
            total_fines = db.session.query(
                func.coalesce(func.sum(Fees.amount), 0)
            ).scalar()
            
            report = {
                'total_books': total_books,
                'total_users': total_users,
                'borrowed_books': borrowed_books,
                'total_fines': float(total_fines),
                'generated_at': datetime.utcnow().isoformat()
            }
        
        elif report_type == 'popular_books':
            # Most popular books
            popular_books = db.session.query(
                Book.title,
                Book.author,
                func.count(BorrowRecord.id).label('borrow_count')
            ).join(BorrowRecord).group_by(Book.id).order_by(
                func.count(BorrowRecord.id).desc()
            ).limit(10).all()
            
            report = [{
                'title': book.title,
                'author': book.author,
                'borrow_count': book.borrow_count
            } for book in popular_books]
        
        elif report_type == 'active_users':
            # Most active users
            active_users = db.session.query(
                User.fullname,
                User.username,
                func.count(BorrowRecord.id).label('borrow_count')
            ).join(BorrowRecord).group_by(User.id).order_by(
                func.count(BorrowRecord.id).desc()
            ).limit(10).all()
            
            report = [{
                'fullname': user.fullname,
                'username': user.username,
                'borrow_count': user.borrow_count
            } for user in active_users]
        
        return jsonify({
            'success': True,
            'report': report,
            'type': report_type
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
