# ========================================
# FICHIER: config.py
# Configuration de l'application
# ========================================

import os

class Config:
    """Configuration centralisée"""
    
    # Secret Key
    SECRET_KEY = 'votre-cle-secrete-super-longue-123456789'
    
    # Upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    
    # PayPal
    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'ARJwJ2EHwHtr_M5gw4myrAjEQ2x_WX8kGVhLiKX2sTr0SWTS-s9fsiXmgMvpNXfjl8i5epJ5Php8QdO-')
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'live')
    
    # Email Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'opaline.parfums@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'VOTRE_APP_PASSWORD_ICI')
    MAIL_DEFAULT_SENDER = 'OPALINE PARFUMS <opaline.parfums@gmail.com>'
    
    # Database
    @staticmethod
    def get_database_uri():
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url or 'sqlite:///perfume_shop.db'
    
    SQLALCHEMY_DATABASE_URI = get_database_uri.__func__()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
