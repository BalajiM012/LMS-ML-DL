#!/usr/bin/env python3
"""
Simple test data insertion for LMS database
"""

from src.app_factory_minimal import create_app, db
from src.models import User, Book, BorrowRecord, Fees
from datetime import datetime, timedelta
import hashlib

def insert_simple_test_data():
    """Insert simple test data into the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data
            print("Clearing existing data...")
            db.session.query(BorrowRecord).delete()
            db.session.query(Fees).delete()
            db.session.query(User).delete()
            db.session.query(Book).delete()
            db.session.commit()

            # Insert sample users
            print("Inserting users...")
            admin_user = User(
                fullname='Admin User',
                username='admin',
                email='admin@lms.com',
                password=hashlib.sha256('admin123'.encode()).hexdigest(),
                role='admin'
            )
            student_user = User(
                fullname='John Student',
                username='student1',
                email='student1@lms.com',
                password=hashlib.sha256('student123'.encode()).hexdigest(),
                role='student'
            )
            db.session.add_all([admin_user, student_user])
            db.session.commit()

            # Insert sample books
            print("Inserting books...")
            book1 = Book(
                title='Python Programming',
                author='John Doe',
                isbn='978-1234567890',
                copies=5,
                total_quantity=5,
                available_quantity=4
            )
            book2 = Book(
                title='Data Structures',
                author='Jane Smith',
                isbn='978-0987654321',
                copies=3,
                total_quantity=3,
                available_quantity=3
            )
            book3 = Book(
                title='Machine Learning',
                author='Alan Turing',
                isbn='978-1122334455',
                copies=2,
                total_quantity=2,
                available_quantity=0
            )
            db.session.add_all([book1, book2, book3])
            db.session.commit()

            # Insert sample borrow records
            print("Inserting borrow records...")
            borrow1 = BorrowRecord(
                user_id=2,
                book_id=1,
                borrow_date=datetime.now() - timedelta(days=10),
                due_date=datetime.now() + timedelta(days=4),
                return_date=None,
                fine=0.0
            )
            borrow2 = BorrowRecord(
                user_id=2,
                book_id=2,
                borrow_date=datetime.now() - timedelta(days=20),
                due_date=datetime.now() - timedelta(days=5),
                return_date=datetime.now() - timedelta(days=3),
                fine=5.0
            )
            db.session.add_all([borrow1, borrow2])
            db.session.commit()

            # Insert sample fees
            print("Inserting fees...")
            fee1 = Fees(
                user_id=2,
                date=datetime.now() - timedelta(days=3),
                amount=5.0,
                reason='Late return'
            )
            fee2 = Fees(
                user_id=2,
                date=datetime.now() - timedelta(days=1),
                amount=10.0,
                reason='Book damage'
            )
            db.session.add_all([fee1, fee2])
            db.session.commit()
            
            print("✅ Test data inserted successfully!")
            print(f"   - {User.query.count()} users")
            print(f"   - {Book.query.count()} books")
            print(f"   - {BorrowRecord.query.count()} borrow records")
            print(f"   - {Fees.query.count()} fees")
            
        except Exception as e:
            print(f"❌ Error inserting test data: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    insert_simple_test_data()
