# app/auth.py

from flask import session, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Admin
from app import db

def login_admin(email, password):
    admin = Admin.query.first()
    if admin and check_password_hash(admin.password_hash, password):
        session['admin_logged_in'] = True
        return True
    return False

def logout_admin():
    session.pop('admin_logged_in', None)

def is_logged_in():
    return session.get('admin_logged_in')
