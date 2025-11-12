import os

class Config:
    SECRET_KEY = 'votre-cle-secrete-super-longue-123456789'

    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max

    PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', 'AfYL5NT82add83YEaYavbcSWW-KxYXH2PU3aThFXZsu8ZcvA-biUwdy8Ra1qyaxvO1YQaqXmpEiqbp5q')
    PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'opaline.parfums@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'uznuwxgbaspghwgu')
    MAIL_DEFAULT_SENDER = 'OPALINE PARFUMS <opaline.parfums@gmail.com>'

    RESEND_API_KEY = os.environ.get('RESEND_API_KEY', 're_bqZgxv8L_9j1JvSJKzYRUfh3S7zFPMAJv')

    @staticmethod
    def get_database_uri():
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url or 'sqlite:///perfume_shop.db'
    
    SQLALCHEMY_DATABASE_URI = get_database_uri.__func__()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ✅ SSL SEULEMENT SI POSTGRESQL (pas en local avec SQLite)
    @staticmethod
    def get_engine_options():
        database_url = os.environ.get('DATABASE_URL')
        
        # Si on utilise PostgreSQL (Render), ajouter les options SSL
        if database_url and 'postgresql://' in database_url:
            return {
                'pool_pre_ping': True,
                'pool_recycle': 300,
                'connect_args': {
                    'sslmode': 'require',
                    'connect_timeout': 10,
                }
            }
        
        # Si SQLite (local), pas d'options spéciales
        return {}
    
    SQLALCHEMY_ENGINE_OPTIONS = get_engine_options.__func__()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}