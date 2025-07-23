#!/usr/bin/env python3
"""
Test data insertion script for LMS database - Exact schema match
"""

from src.app_factory_minimal import create_app, db
from src.models import User, Book, BorrowRecord, Fees
from datetime import datetime, timedelta
import hashlib

def insert_test_data():
    """Insert test data matching the exact database schema"""
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
            student_user2 = User(
                fullname='Jane Student',
                username='student2',
                email='student2@lms.com',
                password=hashlib.sha256('student123'.encode()).hexdigest(),
                role='student'
            )
            db.session.add_all([admin_user, student_user, student_user2])
            db.session.commit()

            # Insert sample books
            print("Inserting books...")
            books = [
                Book(
                    title='Python Programming',
                    author='John Doe',
                    isbn='978-1234567890',
                    copies=5
                ),
                Book(
                    title='Data Structures',
                    author='Jane Smith',
                    isbn='978-0987654321',
                    copies=3
                ),
                Book(
                    title='Machine Learning',
                    author='Alan Turing',
                    isbn='978-1122334455',
                    copies=2
                ),
                Book(
                    title='Web Development',
                    author='Bob Johnson',
                    isbn='978-2233445566',
                    copies=4
                ),
                Book(
                    title='Database Design',
                    author='Alice Brown',
                    isbn='978-3344556677',
                    copies=3
                )
            ]
            db.session.add_all(books)
            db.session.commit()

            # Insert sample borrow records
            print("Inserting borrow records...")
            borrow_records = [
                BorrowRecord(
                    user_id=2,
                    book_id=1,
                    borrow_date=datetime.now() - timedelta(days=10),
                    due_date=datetime.now() + timedelta(days=4),
                    return_date=None,
                    fine=0.0
                ),
                BorrowRecord(
                    user_id=2,
                    book_id=2,
                    borrow_date=datetime.now() - timedelta(days=20),
                    due_date=datetime.now() - timedelta(days=5),
                    return_date=datetime.now() - timedelta(days=3),
                    fine=5.0
                ),
                BorrowRecord(
                    user_id=3,
                    book_id=3,
                    borrow_date=datetime.now() - timedelta(days=5),
                    due_date=datetime.now() + timedelta(days=9),
                    return_date=None,
                    fine=0.0
                ),
                BorrowRecord(
                    user_id=3,
                    book_id=5,
                    borrow_date=datetime.now() - timedelta(days=15),
                    due_date=datetime.now() - timedelta(days=1),
                    return_date=None,
                    fine=2.0
                )
            ]
            db.session.add_all(borrow_records)
            db.session.commit()

            # Insert sample fees
            print("Inserting fees...")
            fees = [
                Fees(
                    user_id=2,
                    date=datetime.now() - timedelta(days=3),
                    amount=5.0,
                    reason='Late return - Data Structures'
                ),
                Fees(
                    user_id=3,
                    date=datetime.now() - timedelta(days=1),
                    amount=2.0,
                    reason='Late return - Database Design'
                ),
                Fees(
                    user_id=2,
                    date=datetime.now() - timedelta(days=7),
                    amount=10.0,
                    reason='Book damage fee'
                )
            ]
            db.session.add_all(fees)
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
    insert_test_data()
