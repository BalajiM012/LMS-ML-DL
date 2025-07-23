from app import db
from app import User, Book, BorrowRecord, Fees

def setup_database():
    db.create_all()
    print("Database tables created successfully.")

if __name__ == '__main__':
    setup_database()
