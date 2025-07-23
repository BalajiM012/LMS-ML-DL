from app import db, User

def list_users():
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}, Role: {user.role}")

if __name__ == "__main__":
    list_users()
