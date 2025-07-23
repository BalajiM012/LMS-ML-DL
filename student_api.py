from flask import Blueprint, jsonify, request, session
from src.models import db, User, Book, BorrowRecord, Fees
from datetime import datetime, timedelta
from sqlalchemy import func, and_

student_bp = Blueprint('student_api', __name__)

@student_bp.route('/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    """Get comprehensive dashboard data for a student"""
    try:
        # Verify user is accessing their own data
        if 'user_id' not in session or session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get user info
        user = User.query.get_or_404(user_id)
        if user.role != 'student':
            return jsonify({'error': 'Access denied'}), 403
        
        # Count borrowed books
        borrowed_count = BorrowRecord.query.filter_by(
            user_id=user_id,
            return_date=None
        ).count()
        
        # Count available books
        available_count = Book.query.filter(
            Book.available_quantity > 0
        ).count()
        
        # Count overdue books
        overdue_count = BorrowRecord.query.filter(
            and_(
                BorrowRecord.user_id == user_id,
                BorrowRecord.return_date.is_(None),
                BorrowRecord.due_date < datetime.utcnow()
            )
        ).count()
        
        # Calculate total fines
        total_fines = db.session.query(
            func.coalesce(func.sum(Fees.amount), 0)
        ).filter_by(user_id=user_id).scalar()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'username': user.username
            },
            'borrowedCount': borrowed_count,
            'availableCount': available_count,
            'overdueCount': overdue_count,
            'totalFines': float(total_fines)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/activity/<int:user_id>', methods=['GET'])
def get_recent_activity(user_id):
    """Get recent activity for a student"""
    try:
        # Verify user is accessing their own data
        if 'user_id' not in session or session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Get recent borrow records
        recent_borrows = BorrowRecord.query.filter_by(
            user_id=user_id
        ).order_by(
            BorrowRecord.borrow_date.desc()
        ).limit(5).all()
        
        # Get recent fees
        recent_fees = Fees.query.filter_by(
            user_id=user_id
        ).order_by(
            Fees.date.desc()
        ).limit(3).all()
        
        activities = []
        
        # Add borrow activities
        for record in recent_borrows:
            book = Book.query.get(record.book_id)
            activities.append({
                'type': 'borrow',
                'title': 'Book Borrowed',
                'description': f"You borrowed '{book.title}' by {book.author}",
                'date': record.borrow_date.isoformat(),
                'book_id': book.id,
                'due_date': record.due_date.isoformat()
            })
        
        # Add return activities (if returned)
        for record in recent_borrows:
            if record.return_date:
                book = Book.query.get(record.book_id)
                activities.append({
                    'type': 'return',
                    'title': 'Book Returned',
                    'description': f"You returned '{book.title}'",
                    'date': record.return_date.isoformat(),
                    'book_id': book.id
                })
        
        # Add fee activities
        for fee in recent_fees:
            activities.append({
                'type': 'fine',
                'title': 'Fine Applied',
                'description': fee.reason,
                'date': fee.date.isoformat(),
                'amount': float(fee.amount)
            })
        
        # Sort by date and limit to 10
        activities.sort(key=lambda x: x['date'], reverse=True)
        activities = activities[:10]
        
        return jsonify({
            'success': True,
            'activities': activities
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/books/borrowed/<int:user_id>', methods=['GET'])
def get_borrowed_books(user_id):
    """Get all books currently borrowed by a student"""
    try:
        if 'user_id' not in session or session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        borrowed_books = db.session.query(
            BorrowRecord, Book
        ).join(
            Book, BorrowRecord.book_id == Book.id
        ).filter(
            and_(
                BorrowRecord.user_id == user_id,
                BorrowRecord.return_date.is_(None)
            )
        ).all()
        
        books_data = []
        for record, book in borrowed_books:
            days_until_due = (record.due_date - datetime.utcnow()).days
            is_overdue = days_until_due < 0
            
            books_data.append({
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'isbn': book.isbn,
                'borrow_date': record.borrow_date.isoformat(),
                'due_date': record.due_date.isoformat(),
                'days_until_due': days_until_due,
                'is_overdue': is_overdue
            })
        
        return jsonify({
            'success': True,
            'books': books_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/books/available', methods=['GET'])
def get_available_books():
    """Get all available books"""
    try:
        books = Book.query.filter(
            Book.available_quantity > 0
        ).all()
        
        books_data = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'category': book.category,
            'available_quantity': book.available_quantity,
            'total_quantity': book.total_quantity,
            'description': book.description
        } for book in books]
        
        return jsonify({
            'success': True,
            'books': books_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/books/search', methods=['GET'])
def search_books():
    """Search books by title, author, or category"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        books_query = Book.query.filter(Book.available_quantity > 0)
        
        if query:
            books_query = books_query.filter(
                Book.title.ilike(f'%{query}%') |
                Book.author.ilike(f'%{query}%')
            )
        
        if category:
            books_query = books_query.filter(
                Book.category.ilike(f'%{category}%')
            )
        
        books = books_query.all()
        
        books_data = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'category': book.category,
            'available_quantity': book.available_quantity,
            'description': book.description
        } for book in books]
        
        return jsonify({
            'success': True,
            'books': books_data,
            'query': query,
            'category': category
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/books/borrow', methods=['POST'])
def borrow_book():
    """Borrow a book"""
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        
        # Check if book exists and is available
        book = Book.query.get_or_404(book_id)
        if book.available_quantity <= 0:
            return jsonify({'error': 'Book not available'}), 400
        
        # Check if user already has this book
        existing_record = BorrowRecord.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            return_date=None
        ).first()
        
        if existing_record:
            return jsonify({'error': 'You already have this book'}), 400
        
        # Create borrow record
        borrow_record = BorrowRecord(
            user_id=user_id,
            book_id=book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        
        # Update book availability
        book.available_quantity -= 1
        
        db.session.add(borrow_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book borrowed successfully',
            'due_date': borrow_record.due_date.isoformat()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/books/return', methods=['POST'])
def return_book():
    """Return a borrowed book"""
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_id = session['user_id']
        
        # Find the borrow record
        record = BorrowRecord.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            return_date=None
        ).first()
        
        if not record:
            return jsonify({'error': 'Book not found in your borrowed list'}), 404
        
        # Update record
        record.return_date = datetime.utcnow()
        
        # Update book availability
        book = Book.query.get(book_id)
        book.available_quantity += 1
        
        # Calculate fine if overdue
        fine_amount = 0
        if record.due_date < datetime.utcnow():
            days_overdue = (datetime.utcnow() - record.due_date).days
            fine_amount = days_overdue * 1.0  # $1 per day
        
        if fine_amount > 0:
            fine = Fees(
                user_id=user_id,
                date=datetime.utcnow(),
                amount=fine_amount,
                reason=f'Late return for book: {book.title}'
            )
            db.session.add(fine)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Book returned successfully',
            'fine_amount': fine_amount
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@student_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    """Get student profile information"""
    try:
        if 'user_id' not in session or session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user = User.query.get_or_404(user_id)
        
        # Get borrowing statistics
        total_borrowed = BorrowRecord.query.filter_by(user_id=user_id).count()
        currently_borrowed = BorrowRecord.query.filter_by(
            user_id=user_id,
            return_date=None
        ).count()
        
        total_fines = db.session.query(
            func.coalesce(func.sum(Fees.amount), 0)
        ).filter_by(user_id=user_id).scalar()
        
        return jsonify({
            'success': True,
            'profile': {
                'id': user.id,
                'fullname': user.fullname,
                'email': user.email,
                'username': user.username,
                'role': user.role,
                'total_borrowed': total_borrowed,
                'currently_borrowed': currently_borrowed,
                'total_fines': float(total_fines)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@student_bp.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    """Update student profile"""
    try:
        if 'user_id' not in session or session['user_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        
        # Update allowed fields
        if 'fullname' in data:
            user.fullname = data['fullname']
        if 'email' in data:
            user.email = data['email']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
