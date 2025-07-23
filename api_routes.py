from flask import Blueprint, jsonify, request
from src.models import db, Book, Student, Issue
from datetime import datetime, timedelta
import random

# Create a new blueprint for additional API routes
api_bp = Blueprint('api_routes', __name__)

@api_bp.route('/api/stats', methods=['GET'])
def get_library_stats():
    """Get comprehensive library statistics"""
    try:
        total_books = Book.query.count()
        total_students = Student.query.count()
        
        # Books currently issued
        books_issued = Issue.query.filter(
            Issue.return_date.is_(None)
        ).count()
        
        # Available books
        available_books = total_books - books_issued
        
        # Recent activity (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_issues = Issue.query.filter(
            Issue.issue_date >= seven_days_ago
        ).count()
        
        # Popular books (most issued)
        popular_books = db.session.query(
            Book.title,
            db.func.count(Issue.id).label('issue_count')
        ).join(Issue).group_by(Book.id).order_by(
            db.func.count(Issue.id).desc()
        ).limit(5).all()
        
        popular_books_list = [
            {'title': book.title, 'issue_count': book.issue_count}
            for book in popular_books
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'total_books': total_books,
                'total_students': total_students,
                'books_issued': books_issued,
                'available_books': available_books,
                'recent_issues': recent_issues,
                'popular_books': popular_books_list
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/api/books/search', methods=['GET'])
def search_books():
    """Search books by title, author, or category"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        author = request.args.get('author', '')
        
        books_query = Book.query
        
        if query:
            books_query = books_query.filter(
                Book.title.ilike(f'%{query}%') | 
                Book.author.ilike(f'%{query}%')
            )
        
        if category:
            books_query = books_query.filter(Book.category.ilike(f'%{category}%'))
            
        if author:
            books_query = books_query.filter(Book.author.ilike(f'%{author}%'))
        
        books = books_query.limit(20).all()
        
        books_list = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'total_quantity': book.total_quantity,
            'available_quantity': book.available_quantity,
            'isbn': book.isbn
        } for book in books]
        
        return jsonify({
            'success': True,
            'data': books_list,
            'count': len(books_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/api/books/recommendations', methods=['GET'])
def get_recommendations():
    """Get book recommendations for students"""
    try:
        student_id = request.args.get('student_id')
        
        if student_id:
            # Get student's reading history
            student_issues = Issue.query.filter_by(student_id=student_id).all()
            read_books = [issue.book_id for issue in student_issues]
            
            # Get books from same categories as read books
            if read_books:
                categories = db.session.query(Book.category).filter(
                    Book.id.in_(read_books)
                ).distinct().all()
                
                category_list = [cat[0] for cat in categories]
                
                recommendations = Book.query.filter(
                    Book.category.in_(category_list),
                    ~Book.id.in_(read_books),
                    Book.available_quantity > 0
                ).limit(10).all()
            else:
                # Return popular books if no reading history
                recommendations = Book.query.filter(
                    Book.available_quantity > 0
                ).order_by(Book.total_quantity.desc()).limit(10).all()
        else:
            # Return random available books
            recommendations = Book.query.filter(
                Book.available_quantity > 0
            ).order_by(db.func.random()).limit(10).all()
        
        recommendations_list = [{
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'description': book.description or 'No description available',
            'available_quantity': book.available_quantity
        } for book in recommendations]
        
        return jsonify({
            'success': True,
            'data': recommendations_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for the API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@api_bp.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all book categories"""
    try:
        categories = db.session.query(Book.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'data': category_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book_details(book_id):
    """Get detailed information about a specific book"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Get issue history
        issues = Issue.query.filter_by(book_id=book_id).all()
        issue_history = [{
            'student_name': issue.student.name,
            'issue_date': issue.issue_date.isoformat(),
            'return_date': issue.return_date.isoformat() if issue.return_date else None,
            'status': 'Returned' if issue.return_date else 'Issued'
        } for issue in issues]
        
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'category': book.category,
            'isbn': book.isbn,
            'total_quantity': book.total_quantity,
            'available_quantity': book.available_quantity,
            'description': book.description,
            'issue_history': issue_history,
            'current_status': 'Available' if book.available_quantity > 0 else 'Not Available'
        }
        
        return jsonify({
            'success': True,
            'data': book_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

# Additional utility endpoints
@api_bp.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get dashboard summary data for admin"""
    try:
        # Basic counts
        total_books = Book.query.count()
        total_students = Student.query.count()
        active_issues = Issue.query.filter(Issue.return_date.is_(None)).count()
        
        # Overdue books
        overdue_books = Issue.query.filter(
            Issue.return_date.is_(None),
            Issue.due_date < datetime.utcnow()
        ).count()
        
        # Recent activity
        today = datetime.utcnow().date()
        today_issues = Issue.query.filter(
            db.func.date(Issue.issue_date) == today
        ).count()
        
        today_returns = Issue.query.filter(
            db.func.date(Issue.return_date) == today
        ).count()
        
        return jsonify({
            'success': True,
            'data': {
                'total_books': total_books,
                'total_students': total_students,
                'active_issues': active_issues,
                'overdue_books': overdue_books,
                'today_issues': today_issues,
                'today_returns': today_returns
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
