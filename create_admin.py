# create_admin.py

from app import create_app
from app.models import db, Admin
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = input("Enter admin email: ").strip()
    password = input("Enter admin password: ").strip()

    email_hash = generate_password_hash(email)
    password_hash = generate_password_hash(password)

    existing = Admin.query.first()
    if existing:
        print("Admin already exists. Overwriting...")
        db.session.delete(existing)

    admin = Admin(email_hash=email_hash, password_hash=password_hash)
    db.session.add(admin)
    db.session.commit()
    print("✅ Admin user created.")
