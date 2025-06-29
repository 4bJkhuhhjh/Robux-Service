# app/routes.py

import os
from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import Order, Admin, User
from app.auth import login_admin, logout_admin, is_logged_in
from flask import current_app as app
from flask_login import login_user, logout_user, login_required, current_user

UPLOAD_FOLDER = 'app/static/qr_codes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

import math

def calculate_price(robux_requested):
    best_option = None
    max_500_bundles = (robux_requested + 499) // 500 + 1  # Cover slightly more than needed

    for b500 in range(max_500_bundles + 1):
        robux_500 = b500 * 500
        remaining = max(0, robux_requested - robux_500)
        b80 = -(-remaining // 80)  # Equivalent to math.ceil(remaining / 80)

        total_robux = robux_500 + b80 * 80
        total_price = round(b500 * 5 + b80 * 1.09, 2)

        if not best_option or total_price < best_option[1]:
            best_option = (total_robux, (total_price + 1))

    return best_option


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        robux = int(request.form["robux"])
        actual_robux, price = calculate_price(robux)

        order = Order(
            email_hash=generate_password_hash(current_user.email),
            email_plain=current_user.email,
            user_id=current_user.id,
            robux_amount=actual_robux,
            price_usd=price
        )   
        db.session.add(order)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("index.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        if login_admin(email, password):
            return redirect(url_for("admin_dashboard"))
        flash("Login failed")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    logout_admin()
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if not is_logged_in():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        order_id = request.form["order_id"]
        action = request.form["action"]
        order = Order.query.get(order_id)

        if action == "send_qr":
            qr_file = request.files["qr_file"]
            filename = secure_filename(qr_file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            qr_file.save(filepath)
            order.qr_filename = filename
            order.quick_login = request.form['quick_login']
            order.status = "qr_sent"
        elif action == "mark_paid":
            order.status = "paid"
            if order.qr_filename:
                qr_path = os.path.join(UPLOAD_FOLDER, order.qr_filename)
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                order.qr_filename = None
        elif action == "reject":
            order.status = "rejected"
            if order.qr_filename:
                qr_path = os.path.join(UPLOAD_FOLDER, order.qr_filename)
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                order.qr_filename = None
        db.session.commit()
        return redirect(url_for("admin_dashboard", status=request.args.get("status", "")))

    # GET request: apply status filter if provided
    status_filter = request.args.get("status")
    if status_filter:
        orders = Order.query.filter_by(status=status_filter).order_by(Order.timestamp.desc()).all()
    else:
        orders = Order.query.order_by(Order.timestamp.desc()).all()

    return render_template("admin_dashboard.html", orders=orders)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        user = User(email=email, password_hash=password)
        db.session.add(user)
        db.session.commit()
        flash("Registered. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Login failed")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/dashboard", methods=["GET","POST"])
@login_required
def dashboard():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    if request.method == "POST":
        order_id = request.form["order_id"]
        action = request.form["action"]
        order = Order.query.get(order_id)
        if action == "reject":
            if order.qr_filename:
                qr_path = os.path.join(UPLOAD_FOLDER, order.qr_filename)
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                order.qr_filename = None
            order.status = "canceled"
        elif action == "send_2fa":
            ee = request.form["2fa"]
            order.twofa = ee
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("dashboard.html", orders=orders)
