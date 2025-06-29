# config.py

import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "devkey")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_DEFAULT_SENDER = "rokk223kkoa@gmail.com"
    MAIL_USERNAME = "rokk223kkoa@gmail.com"  # Set this in your environment
    MAIL_PASSWORD = "cocknballS21--"
