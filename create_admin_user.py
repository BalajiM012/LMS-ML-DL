from app import db, User
from werkzeug.security import generate_password_hash

def create_admin():
    admin = User(
        fullname="New Admin User",
        email="newadmin@example.com",
        username="newadmin",
        password=generate_password_hash("newadminpassword"),
        role="admin"
    )
    # Remove existing admin with same username or email if any
    existing_admin = User.query.filter((User.username == admin.username) | (User.email == admin.email)).first()
    if existing_admin:
        db.session.delete(existing_admin)
        db.session.commit()
    db.session.add(admin)
    db.session.commit()
    print("New admin user created successfully.")

if __name__ == "__main__":
    from app import app
    with app.app_context():
        create_admin()
