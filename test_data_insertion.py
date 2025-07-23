from src.app_factory import db
from src.models import BorrowRecord, Fees
from datetime import datetime, timedelta

def insert_test_data():
    # Clear existing data
    db.session.query(BorrowRecord).delete()
    db.session.query(Fees).delete()
    db.session.commit()

    # Insert sample borrow records
    borrow1 = BorrowRecord(
        user_id=1,
        book_id=1,
        borrow_date=datetime.now() - timedelta(days=10),
        due_date=datetime.now() + timedelta(days=10),
        return_date=None,
        fine=0.0
    )
    borrow2 = BorrowRecord(
        user_id=1,
        book_id=2,
        borrow_date=datetime.now() - timedelta(days=20),
        due_date=datetime.now() - timedelta(days=5),
        return_date=datetime.now() - timedelta(days=3),
        fine=5.0
    )
    db.session.add_all([borrow1, borrow2])

    # Insert sample fees
    fee1 = Fees(
        user_id=1,
        date=datetime.now() - timedelta(days=3),
        amount=5.0,
        reason='Late return'
    )
    fee2 = Fees(
        user_id=1,
        date=datetime.now() - timedelta(days=1),
        amount=10.0,
        reason='Lost book'
    )
    db.session.add_all([fee1, fee2])

    db.session.commit()
    print("Test data inserted successfully.")

if __name__ == '__main__':
    insert_test_data()
