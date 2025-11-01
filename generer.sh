#!/bin/bash

echo "============================================================"
echo "🚀 GÉNÉRATION STRUCTURE - OPALINE PARFUMS"
echo "============================================================"
echo ""

# Créer les dossiers
echo "📁 Création des dossiers..."
mkdir -p templates/legal
mkdir -p templates/admin
mkdir -p static/uploads
echo "✅ Dossiers créés"
echo ""

# ========================================
# config.py
# ========================================
echo "📝 Création de config.py..."
cat > config.py << 'EOF'
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
EOF
echo "✅ config.py créé"

# ========================================
# models.py
# ========================================
echo "📝 Création de models.py..."
cat > models.py << 'EOF'
# ========================================
# FICHIER: models.py
# Modèles de base de données
# ========================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Admin(UserMixin, db.Model):
    """Compte administrateur"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    """Produit (parfum)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=10)
    category = db.Column(db.String(50))
    size_ml = db.Column(db.Integer)
    image_url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)

class Order(db.Model):
    """Commande client"""
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_first_name = db.Column(db.String(50), nullable=False)
    customer_last_name = db.Column(db.String(50), nullable=False)
    customer_phone = db.Column(db.String(20))
    shipping_address = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_postal_code = db.Column(db.String(20))
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    """Avis client"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    author_name = db.Column(db.String(100), default='Anonyme')
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='reviews')

class OrderItem(db.Model):
    """Article d'une commande"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')
EOF
echo "✅ models.py créé"

# ========================================
# utils.py
# ========================================
echo "📝 Création de utils.py..."
cat > utils.py << 'EOF'
# ========================================
# FICHIER: utils.py
# Fonctions utilitaires
# ========================================

from flask import session
from werkzeug.utils import secure_filename
import uuid
import os

def allowed_file(filename, allowed_extensions):
    """Vérifie si l'extension est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder, allowed_extensions):
    """Sauvegarde un fichier uploadé"""
    if file and allowed_file(file.filename, allowed_extensions):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return f"/{filepath}"
    return None

def get_cart():
    """Récupère le panier"""
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def get_cart_total():
    """Calcule le total du panier"""
    from models import Product
    cart = get_cart()
    total = 0
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            total += product.price * item['quantity']
    return total

def get_cart_items():
    """Récupère les articles du panier avec détails"""
    from models import Product
    cart = get_cart()
    items = []
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': product.price * item['quantity']
            })
    return items
EOF
echo "✅ utils.py créé"

# ========================================
# email_service.py
# ========================================
echo "📝 Création de email_service.py..."
cat > email_service.py << 'EOF'
# ========================================
# FICHIER: email_service.py
# Service d'envoi d'emails
# ========================================

from flask_mail import Message

def send_order_confirmation(mail, order):
    """Envoie un email de confirmation de commande"""
    try:
        # HTML des produits
        products_html = ""
        for item in order.items:
            products_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #ddd;">{item.product.name}</td>
                <td style="padding: 10px; text-align: center; border-bottom: 1px solid #ddd;">{item.quantity}</td>
                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;">{item.product.price:.2f}$</td>
                <td style="padding: 10px; text-align: right; border-bottom: 1px solid #ddd;"><strong>{item.subtotal:.2f}$</strong></td>
            </tr>
            """
        
        # Template email
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
                <div style="background-color: #000000; padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0;">OPALINE PARFUMS</h1>
                </div>
                
                <div style="padding: 40px 30px; background-color: #f9f9f9;">
                    <h2 style="color: #333;">Merci pour votre commande !</h2>
                    <p>Bonjour {order.customer_first_name} {order.customer_last_name},</p>
                    <p>Votre commande a été confirmée avec succès.</p>
                    
                    <div style="background-color: #fff; padding: 25px; border-radius: 8px; margin: 25px 0;">
                        <h3>Commande #{order.order_number}</h3>
                        <p><strong>Date :</strong> {order.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                        
                        <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                            <thead>
                                <tr style="background-color: #f0f0f0;">
                                    <th style="padding: 12px; text-align: left;">Produit</th>
                                    <th style="padding: 12px; text-align: center;">Qté</th>
                                    <th style="padding: 12px; text-align: right;">Prix</th>
                                    <th style="padding: 12px; text-align: right;">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {products_html}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colspan="3" style="padding: 15px 10px; text-align: right; border-top: 2px solid #333;"><strong>TOTAL :</strong></td>
                                    <td style="padding: 15px 10px; text-align: right; border-top: 2px solid #333; font-size: 18px;"><strong>{order.total_amount:.2f}$ CAD</strong></td>
                                </tr>
                            </tfoot>
                        </table>
                        
                        <div style="margin-top: 25px; padding: 15px; background-color: #f9f9f9;">
                            <h4>Adresse de livraison :</h4>
                            <p>{order.shipping_address}</p>
                            <p>{order.shipping_city}, {order.shipping_postal_code}</p>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <p><strong>Email :</strong> {order.customer_email}</p>
                            <p><strong>Téléphone :</strong> {order.customer_phone}</p>
                        </div>
                    </div>
                    
                    <p>Votre commande sera traitée dans les plus brefs délais.</p>
                    <p>Merci de votre confiance !</p>
                    <p><strong>L'équipe OPALINE PARFUMS</strong></p>
                </div>
                
                <div style="background-color: #333; padding: 25px; text-align: center; color: #fff;">
                    <p>© 2025 OPALINE PARFUMS - Tous droits réservés</p>
                    <p>Pour toute question : opaline.parfums@gmail.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=f"Confirmation de commande #{order.order_number} - OPALINE PARFUMS",
            recipients=[order.customer_email],
            html=html_body
        )
        
        mail.send(msg)
        print(f"✅ Email envoyé à {order.customer_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur email: {e}")
        return False
EOF
echo "✅ email_service.py créé"

# ========================================
# templates/base.html
# ========================================
echo "📝 Création de templates/base.html..."
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OPALINE PARFUMS{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary-color: #000000; --secondary-color: #333333; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; }
        .navbar { background: #000000; border-bottom: 1px solid #333; }
        .navbar-brand { font-weight: 700; letter-spacing: 2px; font-size: 1.2rem; }
        .product-card { transition: transform 0.3s; border: 1px solid #e5e5e5; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.15); }
        .btn-primary { background: #000000; border: 1px solid #000000; }
        .btn-primary:hover { background: #333333; border: 1px solid #333333; }
        .hero { background: linear-gradient(135deg, #f5f5f5, #ffffff); padding: 80px 0; }
        .footer { background: #000000; color: white; padding: 40px 0; margin-top: 60px; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">OPALINE PARFUMS</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('index') }}">Accueil</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('catalog') }}">Catalogue</a></li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('view_cart') }}">
                            <i class="fas fa-shopping-cart"></i> Panier
                            {% if session.cart %}<span class="badge bg-danger">{{ session.cart|length }}</span>{% endif %}
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}

    <footer class="footer">
        <div class="container text-center">
            <p>&copy; 2025 OPALINE PARFUMS - Tous droits réservés</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
EOF
echo "✅ templates/base.html créé"

# ========================================
# templates/index.html
# ========================================
echo "📝 Création de templates/index.html..."
cat > templates/index.html << 'EOF'
{% extends "base.html" %}

{% block title %}Accueil - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="hero">
    <div class="container text-center">
        <h1 class="display-3 fw-bold">Découvrez Votre Signature Olfactive</h1>
        <p class="lead">Collection exclusive de parfums de luxe</p>
        <a href="{{ url_for('catalog') }}" class="btn btn-primary btn-lg">
            <i class="fas fa-search"></i> Explorer la Collection
        </a>
    </div>
</div>

<div class="container my-5">
    <h2 class="text-center mb-5">Nos Parfums Sélectionnés</h2>
    <div class="row g-4">
        {% for product in products %}
        <div class="col-md-4">
            <div class="card product-card h-100">
                <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}" style="height: 300px; object-fit: cover;">
                <div class="card-body">
                    <h5>{{ product.name }}</h5>
                    <p class="text-muted">{{ product.brand }}</p>
                    <p>{{ product.description[:80] }}...</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="h5">${{ "%.2f"|format(product.price) }}</span>
                        <a href="{{ url_for('product_detail', id=product.id) }}" class="btn btn-outline-primary">Voir</a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
EOF
echo "✅ templates/index.html créé"

# ========================================
# requirements.txt
# ========================================
echo "📝 Création de requirements.txt..."
cat > requirements.txt << 'EOF'
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-Mail==0.9.1
Flask-Migrate==4.0.5
Werkzeug==3.0.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
EOF
echo "✅ requirements.txt créé"

# ========================================
# .gitignore
# ========================================
echo "📝 Création de .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.db

# Flask
instance/
.webassets-cache

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
static/uploads/*
!static/uploads/.gitkeep
EOF
echo "✅ .gitignore créé"

# ========================================
# README.md
# ========================================
echo "📝 Création de README.md..."
cat > README.md << 'EOF'
# OPALINE PARFUMS - E-commerce

## Structure du Projet

```
projet/
├── config.py              # Configuration
├── models.py              # Modèles BDD
├── utils.py               # Fonctions helper
├── email_service.py       # Service email
├── app.py                 # Application (À CRÉER !)
├── requirements.txt       # Dépendances
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   └── ... (autres à créer)
└── static/
    └── uploads/           # Images
```

## Étapes suivantes

1. ✅ Structure créée par le script
2. ⚠️  CRÉER app.py (copiez depuis votre fichier original)
3. ⚠️  CRÉER les autres templates HTML
4. ⚠️  MODIFIER config.py (App Password Gmail)
5. ✅ Tester localement
6. ✅ Déployer

## Installation

```bash
pip install -r requirements.txt
python app.py
```

## Identifiants Admin

- Username: admin
- Password: admin123
EOF
echo "✅ README.md créé"

# Créer .gitkeep pour uploads
touch static/uploads/.gitkeep

echo ""
echo "============================================================"
echo "✅ STRUCTURE CRÉÉE AVEC SUCCÈS !"
echo "============================================================"
echo ""
echo "📁 Fichiers créés :"
echo "   ✅ config.py"
echo "   ✅ models.py"
echo "   ✅ utils.py"
echo "   ✅ email_service.py"
echo "   ✅ templates/base.html"
echo "   ✅ templates/index.html"
echo "   ✅ requirements.txt"
echo "   ✅ .gitignore"
echo "   ✅ README.md"
echo ""
echo "📁 Dossiers créés :"
echo "   ✅ templates/"
echo "   ✅ templates/legal/"
echo "   ✅ templates/admin/"
echo "   ✅ static/uploads/"
echo ""
echo "⚠️  IL VOUS RESTE À FAIRE :"
echo ""
echo "1. CRÉER app.py"
echo "   Copiez depuis votre fichier original"
echo ""
echo "2. CRÉER les autres templates HTML"
echo "   (catalog.html, product_detail.html, etc.)"
echo ""
echo "3. MODIFIER config.py"
echo "   Ligne 23: Remplacez 'VOTRE_APP_PASSWORD_ICI'"
echo ""
echo "4. INSTALLER :"
echo "   pip install -r requirements.txt"
echo ""
echo "5. LANCER :"
echo "   python app.py"
echo ""
echo "============================================================"
echo "📖 Lisez README.md pour plus d'infos"
echo "============================================================"
echo ""