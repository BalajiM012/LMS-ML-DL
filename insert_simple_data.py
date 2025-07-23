








#!/usr/bin/env python3
"""
Simple test data insertion for LMS database - Exact schema match
"""

from src.app_factory_minimal import create_app, db
from datetime import datetime, timedelta
import hashlib

def insert_simple_data():
    """Insert simple test data into the database"""
    app = create_app()
    
    with app.app_context():
        try:
            # Clear existing data
            print("Clearing existing data...")
            conn = db.engine.connect()
            
            # Insert users directly
            print("Inserting users...")
            conn.execute(db.text("""
                INSERT INTO user (fullname, username, email, password, role) 
                VALUES 
                ('Admin User', 'admin', 'admin@lms.com', :admin_pass, 'admin'),
                ('John Student', 'student1', 'student1@lms.com', :student_pass, 'student'),
                ('Jane Student', 'student2', 'student2@lms.com', :student_pass, 'student')
            """), {
                'admin_pass': hashlib.sha256('admin123'.encode()).hexdigest(),
                'student_pass': hashlib.sha256('student123'.encode()).hexdigest()
            })
            
            # Insert books
            print("Inserting books...")
            conn.execute(db.text("""
                INSERT INTO book (title, author, isbn, copies) 
                VALUES 
                ('Python Programming', 'John Doe', '978-1234567890', 5),
                ('Data Structures', 'Jane Smith', '978-0987654321', 3),
                ('Machine Learning', 'Alan Turing', '978-1122334455', 2),
                ('Web Development', 'Bob Johnson', '978-2233445566', 4),
                ('Database Design', 'Alice Brown', '978-3344556677', 3)
            """))
            
            # Insert borrow records
            print("Inserting borrow records...")
            conn.execute(db.text("""
                INSERT INTO borrow_record (user_id, book_id, borrow_date, due_date, return_date, fine) 
                VALUES 
                (2, 1, datetime('now', '-10 days'), datetime('now', '+4 days'), NULL, 0.0),
                (2, 2, datetime('now', '-20 days'), datetime('now', '-5 days'), datetime('now', '-3 days'), 5.0),
                (3, 3, datetime('now', '-5 days'), datetime('now', '+9 days'), NULL, 0.0),
                (3, 5, datetime('now', '-15 days'), datetime('now', '-1 day'), NULL, 2.0)
            """))
            
            # Insert fees
            print("Inserting fees...")
            conn.execute(db.text("""
                INSERT INTO fees (user_id, date, amount, reason) 
                VALUES 
                (2, datetime('now', '-3 days'), 5.0, 'Late return - Data Structures'),
                (3, datetime('now', '-1 day'), 2.0, 'Late return - Database Design'),
                (2, datetime('now', '-7 days'), 10.0, 'Book damage fee')
            """))
            
            conn.commit()
            conn.close()
            
            print("✅ Test data inserted successfully!")
            
        except Exception as e:
            print(f"❌ Error inserting test data: {e}")
            raise

if __name__ == '__main__':
    insert_simple_data()
