# ========================================
# FICHIER: app.py
# OPALINE PARFUMS - E-commerce avec Avis Clients
# ========================================

from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# ========================================
# CONFIGURATION
# ========================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'votre-cle-secrete-super-longue-123456789'

# Configuration base de données
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///perfume_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# ========================================
# MODÈLES
# ========================================

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Product(db.Model):
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
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    author_name = db.Column(db.String(100), default='Anonyme')
    rating = db.Column(db.Integer, nullable=False)  # 1 à 5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Product', backref='reviews')

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ========================================
# HELPERS
# ========================================

def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']

def get_cart_total():
    cart = get_cart()
    total = 0
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            total += product.price * item['quantity']
    return total

def get_cart_items():
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

# ========================================
# ROUTES PUBLIQUES
# ========================================

@app.route('/')
def index():
    products = Product.query.filter_by(is_active=True).limit(6).all()
    return render_template_string(INDEX_TEMPLATE, products=products)

@app.route('/catalog')
def catalog():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(is_active=True, category=category).all()
    else:
        products = Product.query.filter_by(is_active=True).all()
    return render_template_string(CATALOG_TEMPLATE, products=products, selected_category=category)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template_string(PRODUCT_DETAIL_TEMPLATE, product=product)

@app.route('/product/<int:id>/review', methods=['POST'])
def add_review(id):
    product = Product.query.get_or_404(id)
    
    author_name = request.form.get('author_name', '').strip()
    if not author_name:
        author_name = 'Anonyme'
    
    review = Review(
        product_id=id,
        author_name=author_name,
        rating=int(request.form['rating']),
        comment=request.form['comment']
    )
    
    db.session.add(review)
    db.session.commit()
    
    flash('Merci pour votre avis !', 'success')
    return redirect(url_for('product_detail', id=id))

@app.route('/cart')
def view_cart():
    items = get_cart_items()
    total = get_cart_total()
    return render_template_string(CART_TEMPLATE, items=items, total=total)

@app.route('/add-to-cart/<int:product_id>')
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = get_cart()
    
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            session.modified = True
            flash(f'{product.name} ajouté au panier!', 'success')
            return redirect(request.referrer or url_for('catalog'))
    
    cart.append({'product_id': product_id, 'quantity': 1})
    session.modified = True
    flash(f'{product.name} ajouté au panier!', 'success')
    return redirect(request.referrer or url_for('catalog'))

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    cart = get_cart()
    cart[:] = [item for item in cart if item['product_id'] != product_id]
    session.modified = True
    flash('Produit retiré du panier', 'info')
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if not get_cart():
        flash('Votre panier est vide', 'warning')
        return redirect(url_for('catalog'))
    
    if request.method == 'POST':
        order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.query.count() + 1:03d}"
        
        order = Order(
            order_number=order_number,
            customer_email=request.form['email'],
            customer_first_name=request.form['first_name'],
            customer_last_name=request.form['last_name'],
            customer_phone=request.form['phone'],
            shipping_address=request.form['address'],
            shipping_city=request.form['city'],
            shipping_postal_code=request.form['postal_code'],
            total_amount=get_cart_total(),
            status='paid'
        )
        
        db.session.add(order)
        db.session.commit()
        
        session['cart'] = []
        session.modified = True
        
        flash(f'Commande {order_number} confirmée! Merci pour votre achat.', 'success')
        return redirect(url_for('order_success', order_number=order_number))
    
    items = get_cart_items()
    total = get_cart_total()
    return render_template_string(CHECKOUT_TEMPLATE, items=items, total=total)

@app.route('/order-success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template_string(ORDER_SUCCESS_TEMPLATE, order=order)

# ========================================
# ROUTES ADMIN
# ========================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form['username']).first()
        if admin and check_password_hash(admin.password_hash, request.form['password']):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        flash('Identifiants incorrects', 'danger')
    return render_template_string(ADMIN_LOGIN_TEMPLATE)

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    pending_orders = Order.query.filter_by(status='pending').count()
    total_products = Product.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    return render_template_string(ADMIN_DASHBOARD_TEMPLATE, 
                                 total_orders=total_orders,
                                 total_revenue=total_revenue,
                                 pending_orders=pending_orders,
                                 total_products=total_products,
                                 recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.all()
    return render_template_string(ADMIN_PRODUCTS_TEMPLATE, products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            brand=request.form['brand'],
            description=request.form['description'],
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            category=request.form['category'],
            size_ml=int(request.form['size_ml']),
            image_url=request.form['image_url']
        )
        db.session.add(product)
        db.session.commit()
        flash('Produit ajouté avec succès!', 'success')
        return redirect(url_for('admin_products'))
    return render_template_string(ADMIN_ADD_PRODUCT_TEMPLATE)

@app.route('/admin/products/delete/<int:id>')
@login_required
def admin_delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produit supprimé', 'success')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template_string(ADMIN_ORDERS_TEMPLATE, orders=orders)

@app.route('/admin/orders/<int:id>/status', methods=['POST'])
@login_required
def admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    order.status = request.form['status']
    db.session.commit()
    flash('Statut mis à jour', 'success')
    return redirect(url_for('admin_orders'))

# ========================================
# TEMPLATES HTML
# ========================================

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}OPALINE PARFUMS{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #000000;
            --secondary-color: #333333;
        }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; }
        .navbar { background: #000000; border-bottom: 1px solid #333; }
        .navbar-brand { font-weight: 700; letter-spacing: 2px; font-size: 1.2rem; }
        .product-card { transition: transform 0.3s; border: 1px solid #e5e5e5; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 5px 20px rgba(0,0,0,0.15); }
        .btn-primary { background: #000000; border: 1px solid #000000; }
        .btn-primary:hover { background: #333333; border: 1px solid #333333; }
        .btn-outline-primary { color: #000000; border: 1px solid #000000; }
        .btn-outline-primary:hover { background: #000000; color: white; }
        .btn-outline-primary.active { background: #000000; color: white; }
        .hero { background: linear-gradient(135deg, #f5f5f5, #ffffff); padding: 80px 0; border-bottom: 1px solid #e5e5e5; }
        .footer { background: #000000; color: white; padding: 40px 0; margin-top: 60px; }
        .badge { background: #000000 !important; }
        .text-primary { color: #000000 !important; }
        .alert-success { background-color: #f0f0f0; border-color: #000000; color: #000000; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="{{ url_for('index') }}">
                <img src="https://i.ibb.co/jtSLs1S/IMG-20251018-181823.png" alt="Logo OPALINE" style="height: 50px; margin-right: 12px;">
                OPALINE PARFUMS
            </a>
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
                    {% if current_user.is_authenticated %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_dashboard') }}">Admin</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin_logout') }}">Déconnexion</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container mt-3">
                {% for category, message in messages %}
                <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
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
            <p class="mb-1" style="letter-spacing: 2px; font-size: 1.1rem;">OPALINE PARFUMS</p>
            <p class="mb-0">&copy; 2025 Tous droits réservés.</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

INDEX_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="hero">
    <div class="container text-center">
        <h1 class="display-3 fw-bold mb-4" style="color: #000;">Découvrez Votre Signature Olfactive</h1>
        <p class="lead mb-4" style="color: #333;">Collection exclusive de parfums de luxe</p>
        <a href="{{ url_for('catalog') }}" class="btn btn-primary btn-lg px-5">
            <i class="fas fa-search"></i> Explorer la Collection
        </a>
    </div>
</div>

<div class="container my-5">
    <h2 class="text-center mb-5" style="letter-spacing: 2px;">NOS PARFUMS VEDETTES</h2>
    <div class="row g-4">
        {% for product in products %}
        <div class="col-md-4">
            <div class="card product-card h-100">
                <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}" style="height: 300px; object-fit: cover;">
                <div class="card-body">
                    <span class="badge mb-2">{{ product.category }}</span>
                    <h5 class="card-title">{{ product.name }}</h5>
                    <p class="text-muted mb-2">{{ product.brand }}</p>
                    
                    {% set avg_rating = product.reviews|map(attribute='rating')|sum / product.reviews|length if product.reviews|length > 0 else 0 %}
                    {% if product.reviews|length > 0 %}
                    <div class="mb-2">
                        <span style="color: gold; font-size: 0.9rem;">
                            {% for i in range(5) %}
                                {% if i < avg_rating|round %}★{% else %}☆{% endif %}
                            {% endfor %}
                        </span>
                        <small class="text-muted">({{ product.reviews|length }})</small>
                    </div>
                    {% endif %}
                    
                    <p class="card-text text-truncate">{{ product.description }}</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <h4 class="text-primary mb-0">{{ "%.2f"|format(product.price) }}€</h4>
                        <a href="{{ url_for('add_to_cart', product_id=product.id) }}" class="btn btn-primary">
                            <i class="fas fa-cart-plus"></i> Ajouter
                        </a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
''')

CATALOG_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4">Notre Catalogue</h2>
    
    <div class="mb-4">
        <a href="{{ url_for('catalog') }}" class="btn btn-outline-primary {% if not selected_category %}active{% endif %}">Tous</a>
        <a href="{{ url_for('catalog', category='Homme') }}" class="btn btn-outline-primary {% if selected_category == 'Homme' %}active{% endif %}">Homme</a>
        <a href="{{ url_for('catalog', category='Femme') }}" class="btn btn-outline-primary {% if selected_category == 'Femme' %}active{% endif %}">Femme</a>
        <a href="{{ url_for('catalog', category='Unisexe') }}" class="btn btn-outline-primary {% if selected_category == 'Unisexe' %}active{% endif %}">Unisexe</a>
    </div>

    <div class="row g-4">
        {% for product in products %}
        <div class="col-md-3">
            <div class="card product-card h-100">
                <a href="{{ url_for('product_detail', id=product.id) }}" style="text-decoration: none; color: inherit;">
                    <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}" style="height: 250px; object-fit: cover;">
                    <div class="card-body">
                        <span class="badge mb-2">{{ product.category }}</span>
                        <h6 class="card-title">{{ product.name }}</h6>
                        <p class="text-muted small mb-2">{{ product.brand }} - {{ product.size_ml }}ml</p>
                        
                        {% set avg_rating = product.reviews|map(attribute='rating')|sum / product.reviews|length if product.reviews|length > 0 else 0 %}
                        {% if product.reviews|length > 0 %}
                        <div class="mb-2">
                            <span style="color: gold; font-size: 0.8rem;">
                                {% for i in range(5) %}
                                    {% if i < avg_rating|round %}★{% else %}☆{% endif %}
                                {% endfor %}
                            </span>
                            <small class="text-muted">({{ product.reviews|length }})</small>
                        </div>
                        {% endif %}
                        
                        <div class="d-flex justify-content-between align-items-center">
                            <h5 class="text-primary mb-0">{{ "%.2f"|format(product.price) }}€</h5>
                            <a href="{{ url_for('add_to_cart', product_id=product.id) }}" class="btn btn-sm btn-primary" onclick="event.stopPropagation();">
                                <i class="fas fa-cart-plus"></i>
                            </a>
                        </div>
                    </div>
                </a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
''')

PRODUCT_DETAIL_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <div class="row">
        <div class="col-md-6">
            <img src="{{ product.image_url }}" class="img-fluid rounded" alt="{{ product.name }}">
        </div>
        <div class="col-md-6">
            <span class="badge mb-3">{{ product.category }}</span>
            <h2>{{ product.name }}</h2>
            <h4 class="text-muted mb-3">{{ product.brand }}</h4>
            
            {% set avg_rating = product.reviews|map(attribute='rating')|sum / product.reviews|length if product.reviews|length > 0 else 0 %}
            {% if product.reviews|length > 0 %}
            <div class="mb-3">
                <span style="color: gold; font-size: 1.2rem;">
                    {% for i in range(5) %}
                        {% if i < avg_rating|round %}★{% else %}☆{% endif %}
                    {% endfor %}
                </span>
                <span class="text-muted">({{ product.reviews|length }} avis - {{ "%.1f"|format(avg_rating) }}/5)</span>
            </div>
            {% endif %}
            
            <h3 class="text-primary mb-4">{{ "%.2f"|format(product.price) }}€</h3>
            <p class="mb-4">{{ product.description }}</p>
            <p><strong>Taille:</strong> {{ product.size_ml }}ml</p>
            <p><strong>Stock:</strong> {{ product.stock }} disponible(s)</p>
            <a href="{{ url_for('add_to_cart', product_id=product.id) }}" class="btn btn-primary btn-lg mt-3">
                <i class="fas fa-cart-plus"></i> Ajouter au Panier
            </a>
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-12">
            <h3 class="mb-4">Avis Clients</h3>
            
            <div class="card mb-4">
                <div class="card-header"><h5>Laisser un avis</h5></div>
                <div class="card-body">
                    <form method="POST" action="{{ url_for('add_review', id=product.id) }}">
                        <div class="mb-3">
                            <label class="form-label">Nom et Prénom (optionnel)</label>
                            <input type="text" class="form-control" name="author_name" placeholder="Laissez vide pour rester anonyme">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Note *</label>
                            <div class="star-rating">
                                <input type="radio" id="star5" name="rating" value="5" required>
                                <label for="star5">★</label>
                                <input type="radio" id="star4" name="rating" value="4">
                                <label for="star4">★</label>
                                <input type="radio" id="star3" name="rating" value="3">
                                <label for="star3">★</label>
                                <input type="radio" id="star2" name="rating" value="2">
                                <label for="star2">★</label>
                                <input type="radio" id="star1" name="rating" value="1">
                                <label for="star1">★</label>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Votre avis *</label>
                            <textarea class="form-control" name="comment" rows="4" required placeholder="Partagez votre expérience avec ce parfum..."></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">Publier mon avis</button>
                    </form>
                </div>
            </div>
            
            {% if product.reviews %}
            <div class="reviews-list">
                {% for review in product.reviews|reverse %}
                <div class="card mb-3">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1"><strong>{{ review.author_name }}</strong></h6>
                                <div class="mb-2">
                                    <span style="color: gold;">
                                        {% for i in range(review.rating) %}★{% endfor %}
                                        {% for i in range(5 - review.rating) %}☆{% endfor %}
                                    </span>
                                </div>
                                <p class="mb-0">{{ review.comment }}</p>
                            </div>
                            <small class="text-muted">{{ review.created_at.strftime('%d/%m/%Y') }}</small>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <p class="text-muted">Aucun avis pour le moment. Soyez le premier à donner votre avis !</p>
            {% endif %}
        </div>
    </div>
</div>

<style>
.star-rating {
    direction: rtl;
    display: inline-flex;
    font-size: 2rem;
}
.star-rating input {
    display: none;
}
.star-rating label {
    color: #ddd;
    cursor: pointer;
    margin: 0 2px;
}
.star-rating input:checked ~ label,
.star-rating label:hover,
.star-rating label:hover ~ label {
    color: gold;
}
</style>
{% endblock %}
''')

CART_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4">Mon Panier</h2>
    {% if items %}
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>Produit</th>
                    <th>Prix</th>
                    <th>Quantité</th>
                    <th>Sous-total</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>
                        <div class="d-flex align-items-center">
                            <img src="{{ item.product.image_url }}" style="width: 60px; height: 60px; object-fit: cover;" class="me-3 rounded">
                            <div>
                                <strong>{{ item.product.name }}</strong><br>
                                <small class="text-muted">{{ item.product.brand }}</small>
                            </div>
                        </div>
                    </td>
                    <td>{{ "%.2f"|format(item.product.price) }}€</td>
                    <td>{{ item.quantity }}</td>
                    <td><strong>{{ "%.2f"|format(item.subtotal) }}€</strong></td>
                    <td>
                        <a href="{{ url_for('remove_from_cart', product_id=item.product.id) }}" class="btn btn-sm btn-danger">
                            <i class="fas fa-trash"></i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="3" class="text-end"><h4>Total:</h4></td>
                    <td colspan="2"><h4 class="text-primary">{{ "%.2f"|format(total) }}€</h4></td>
                </tr>
            </tfoot>
        </table>
    </div>
    <div class="text-end">
        <a href="{{ url_for('catalog') }}" class="btn btn-outline-secondary">Continuer mes Achats</a>
        <a href="{{ url_for('checkout') }}" class="btn btn-primary btn-lg">Commander <i class="fas fa-arrow-right"></i></a>
    </div>
    {% else %}
    <div class="alert alert-info">
        <i class="fas fa-shopping-cart"></i> Votre panier est vide.
        <a href="{{ url_for('catalog') }}" class="alert-link">Découvrir nos produits</a>
    </div>
    {% endif %}
</div>
{% endblock %}
''')

CHECKOUT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4">Finaliser la Commande</h2>
    <div class="row">
        <div class="col-md-8">
            <form method="POST">
                <div class="card mb-4">
                    <div class="card-header"><h5>Informations Client</h5></div>
                    <div class="card-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Prénom *</label>
                                <input type="text" class="form-control" name="first_name" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Nom *</label>
                                <input type="text" class="form-control" name="last_name" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email *</label>
                            <input type="email" class="form-control" name="email" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Téléphone *</label>
                            <input type="tel" class="form-control" name="phone" required>
                        </div>
                    </div>
                </div>

                <div class="card mb-4">
                    <div class="card-header"><h5>Adresse de Livraison</h5></div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Adresse *</label>
                            <input type="text" class="form-control" name="address" required>
                        </div>
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Ville *</label>
                                <input type="text" class="form-control" name="city" required>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Code Postal *</label>
                                <input type="text" class="form-control" name="postal_code" required>
                            </div>
                        </div>
                    </div>
                </div>

                <button type="submit" class="btn btn-primary btn-lg w-100">
                    <i class="fas fa-credit-card"></i> Payer {{ "%.2f"|format(total) }}€
                </button>
            </form>
        </div>

        <div class="col-md-4">
            <div class="card">
                <div class="card-header"><h5>Récapitulatif</h5></div>
                <div class="card-body">
                    {% for item in items %}
                    <div class="d-flex justify-content-between mb-2">
                        <span>{{ item.product.name }} x{{ item.quantity }}</span>
                        <span>{{ "%.2f"|format(item.subtotal) }}€</span>
                    </div>
                    {% endfor %}
                    <hr>
                    <div class="d-flex justify-content-between">
                        <strong>Total:</strong>
                        <strong class="text-primary">{{ "%.2f"|format(total) }}€</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')

ORDER_SUCCESS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5 text-center">
    <div class="mb-4">
        <i class="fas fa-check-circle" style="font-size: 80px; color: #000;"></i>
    </div>
    <h2>Commande Confirmée!</h2>
    <p class="lead">Merci pour votre achat</p>
    <div class="card mx-auto" style="max-width: 500px;">
        <div class="card-body">
            <h4>Numéro de commande: {{ order.order_number }}</h4>
            <p class="mb-2">Total: <strong>{{ "%.2f"|format(order.total_amount) }}€</strong></p>
            <p class="text-muted">Un email de confirmation a été envoyé à {{ order.customer_email }}</p>
        </div>
    </div>
    <a href="{{ url_for('catalog') }}" class="btn btn-primary mt-4">Retour au Catalogue</a>
</div>
{% endblock %}
''')

ADMIN_LOGIN_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <div class="row justify-content-center">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header text-center">
                    <h4><i class="fas fa-lock"></i> Admin Login</h4>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Username</label>
                            <input type="text" class="form-control" name="username" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Password</label>
                            <input type="password" class="form-control" name="password" required>
                        </div>
                        <button type="submit" class="btn btn-primary w-100">Se Connecter</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')

ADMIN_DASHBOARD_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4"><i class="fas fa-tachometer-alt"></i> Dashboard Admin</h2>
    
    <div class="row g-4 mb-5">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h3 class="text-primary">{{ total_orders }}</h3>
                    <p class="text-muted">Commandes Totales</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h3 style="color: #000;">{{ "%.2f"|format(total_revenue) }}€</h3>
                    <p class="text-muted">Chiffre d'Affaires</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h3 style="color: #666;">{{ pending_orders }}</h3>
                    <p class="text-muted">En Attente</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h3 style="color: #333;">{{ total_products }}</h3>
                    <p class="text-muted">Produits</p>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header"><h5>Commandes Récentes</h5></div>
                <div class="card-body">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>N°</th>
                                <th>Client</th>
                                <th>Total</th>
                                <th>Statut</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for order in recent_orders %}
                            <tr>
                                <td>{{ order.order_number }}</td>
                                <td>{{ order.customer_first_name }} {{ order.customer_last_name }}</td>
                                <td>{{ "%.2f"|format(order.total_amount) }}€</td>
                                <td><span class="badge">{{ order.status }}</span></td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class="col-md-6">
            <div class="card">
                <div class="card-header"><h5>Actions Rapides</h5></div>
                <div class="card-body">
                    <a href="{{ url_for('admin_add_product') }}" class="btn btn-primary w-100 mb-2">
                        <i class="fas fa-plus"></i> Ajouter un Produit
                    </a>
                    <a href="{{ url_for('admin_products') }}" class="btn btn-outline-primary w-100 mb-2">
                        <i class="fas fa-box"></i> Gérer les Produits
                    </a>
                    <a href="{{ url_for('admin_orders') }}" class="btn btn-outline-primary w-100">
                        <i class="fas fa-shopping-bag"></i> Voir les Commandes
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''')

ADMIN_PRODUCTS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fas fa-box"></i> Gestion des Produits</h2>
        <a href="{{ url_for('admin_add_product') }}" class="btn btn-primary">
            <i class="fas fa-plus"></i> Nouveau Produit
        </a>
    </div>

    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>Image</th>
                    <th>Nom</th>
                    <th>Marque</th>
                    <th>Catégorie</th>
                    <th>Prix</th>
                    <th>Stock</th>
                    <th>Avis</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for product in products %}
                <tr>
                    <td><img src="{{ product.image_url }}" style="width: 50px; height: 50px; object-fit: cover;" class="rounded"></td>
                    <td>{{ product.name }}</td>
                    <td>{{ product.brand }}</td>
                    <td><span class="badge">{{ product.category }}</span></td>
                    <td>{{ "%.2f"|format(product.price) }}€</td>
                    <td>
                        {% if product.stock < 5 %}
                        <span class="badge bg-danger">{{ product.stock }}</span>
                        {% else %}
                        <span class="badge">{{ product.stock }}</span>
                        {% endif %}
                    </td>
                    <td>
                        {% set avg_rating = product.reviews|map(attribute='rating')|sum / product.reviews|length if product.reviews|length > 0 else 0 %}
                        {% if product.reviews|length > 0 %}
                        <span style="color: gold;">★ {{ "%.1f"|format(avg_rating) }}</span> ({{ product.reviews|length }})
                        {% else %}
                        <span class="text-muted">Aucun</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{{ url_for('admin_delete_product', id=product.id) }}" 
                           class="btn btn-sm btn-danger"
                           onclick="return confirm('Supprimer ce produit?')">
                            <i class="fas fa-trash"></i>
                        </a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''')

ADMIN_ADD_PRODUCT_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4"><i class="fas fa-plus"></i> Ajouter un Produit</h2>
    
    <form method="POST">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label class="form-label">Nom du Produit *</label>
                    <input type="text" class="form-control" name="name" required>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label class="form-label">Marque *</label>
                    <input type="text" class="form-control" name="brand" required>
                </div>
            </div>
        </div>

        <div class="mb-3">
            <label class="form-label">Description *</label>
            <textarea class="form-control" name="description" rows="3" required></textarea>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div class="mb-3">
                    <label class="form-label">Prix (€) *</label>
                    <input type="number" step="0.01" class="form-control" name="price" required>
                </div>
            </div>
            <div class="col-md-4">
                <div class="mb-3">
                    <label class="form-label">Stock *</label>
                    <input type="number" class="form-control" name="stock" value="10" required>
                </div>
            </div>
            <div class="col-md-4">
                <div class="mb-3">
                    <label class="form-label">Taille (ml) *</label>
                    <select class="form-select" name="size_ml" required>
                        <option value="30">30ml</option>
                        <option value="50" selected>50ml</option>
                        <option value="100">100ml</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label class="form-label">Catégorie *</label>
                    <select class="form-select" name="category" required>
                        <option value="Homme">Homme</option>
                        <option value="Femme">Femme</option>
                        <option value="Unisexe">Unisexe</option>
                    </select>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label class="form-label">URL Image *</label>
                    <input type="url" class="form-control" name="image_url" 
                           placeholder="https://example.com/image.jpg" required>
                </div>
            </div>
        </div>

        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary">
                <i class="fas fa-save"></i> Enregistrer
            </button>
            <a href="{{ url_for('admin_products') }}" class="btn btn-outline-primary">Annuler</a>
        </div>
    </form>
</div>
{% endblock %}
''')

ADMIN_ORDERS_TEMPLATE = BASE_TEMPLATE.replace('{% block content %}{% endblock %}', '''
{% block content %}
<div class="container my-5">
    <h2 class="mb-4"><i class="fas fa-shopping-bag"></i> Gestion des Commandes</h2>

    <div class="table-responsive">
        <table class="table table-hover">
            <thead>
                <tr>
                    <th>N° Commande</th>
                    <th>Client</th>
                    <th>Email</th>
                    <th>Total</th>
                    <th>Statut</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                {% for order in orders %}
                <tr>
                    <td><strong>{{ order.order_number }}</strong></td>
                    <td>{{ order.customer_first_name }} {{ order.customer_last_name }}</td>
                    <td>{{ order.customer_email }}</td>
                    <td>{{ "%.2f"|format(order.total_amount) }}€</td>
                    <td>
                        <form method="POST" action="{{ url_for('admin_update_order_status', id=order.id) }}" style="display:inline;">
                            <select name="status" class="form-select form-select-sm" onchange="this.form.submit()">
                                <option value="pending" {% if order.status == 'pending' %}selected{% endif %}>En attente</option>
                                <option value="paid" {% if order.status == 'paid' %}selected{% endif %}>Payé</option>
                                <option value="processing" {% if order.status == 'processing' %}selected{% endif %}>Traitement</option>
                                <option value="shipped" {% if order.status == 'shipped' %}selected{% endif %}>Expédié</option>
                                <option value="delivered" {% if order.status == 'delivered' %}selected{% endif %}>Livré</option>
                            </select>
                        </form>
                    </td>
                    <td>{{ order.created_at.strftime('%d/%m/%Y') }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''')

# ========================================
# INITIALISATION & DONNÉES DE TEST
# ========================================

def init_db():
    """Initialise la base de données avec des données de test"""
    with app.app_context():
        db.create_all()
        print("✅ Tables vérifiées/créées")
        
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin créé: username='admin', password='admin123'")
        
        if Product.query.count() == 0:
            demo_products = [
                Product(name="Noir Extrême", brand="Tom Ford", description="Un parfum oriental boisé intense et sophistiqué pour homme", price=145.00, stock=15, category="Homme", size_ml=100, image_url="https://images.unsplash.com/photo-1541643600914-78b084683601?w=500"),
                Product(name="La Vie Est Belle", brand="Lancôme", description="L'essence du bonheur dans un flacon, notes florales et gourmandes", price=98.00, stock=20, category="Femme", size_ml=50, image_url="https://images.unsplash.com/photo-1588405748880-12d1d2a59cca?w=500"),
                Product(name="Sauvage", brand="Dior", description="Frais, brut et noble. Un parfum puissant inspiré par les grands espaces", price=89.00, stock=25, category="Homme", size_ml=100, image_url="https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=500"),
                Product(name="Good Girl", brand="Carolina Herrera", description="Audacieux et élégant, mélange de notes florales et ambrées", price=112.00, stock=12, category="Femme", size_ml=80, image_url="https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=500"),
                Product(name="Aventus", brand="Creed", description="Un parfum frais et fruité célébrant la force et la vision", price=285.00, stock=8, category="Homme", size_ml=100, image_url="https://images.unsplash.com/photo-1594035910387-fea47794261f?w=500"),
                Product(name="Black Opium", brand="Yves Saint Laurent", description="Addiction sensuelle au café noir et à la vanille blanche", price=95.00, stock=18, category="Femme", size_ml=50, image_url="https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=500"),
                Product(name="Oud Wood", brand="Tom Ford", description="Rare oud associé à des épices exotiques et du bois précieux", price=195.00, stock=10, category="Unisexe", size_ml=50, image_url="https://images.unsplash.com/photo-1528740561666-dc2479dc08ab?w=500"),
                Product(name="J'adore", brand="Dior", description="Bouquet floral féminin et sensuel aux notes d'ylang-ylang", price=105.00, stock=22, category="Femme", size_ml=100, image_url="https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=500")
            ]
            for product in demo_products:
                db.session.add(product)
            db.session.commit()
            print(f"✅ {len(demo_products)} produits de démonstration créés")

# Initialiser la DB au démarrage
init_db()

if __name__ == '__main__':    
    print("\n" + "="*50)
    print("🚀 OPALINE PARFUMS - SERVEUR DÉMARRÉ!")
    print("="*50)
    print("\n📱 Accès:")
    print("   Site Public: http://localhost:5000")
    print("   Admin Panel: http://localhost:5000/admin/login")
    print("\n🔑 Identifiants Admin:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)