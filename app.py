# ========================================
# FICHIER: app.py (VERSION AVEC TEMPLATES/)
# Application principale - Utilise render_template
# ========================================

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

# Imports des modules
from config import Config, ALLOWED_EXTENSIONS
from models import db, Admin, Product, Order, OrderItem, Review
from utils import get_cart, get_cart_total, get_cart_items, save_uploaded_file
from email_service import send_order_confirmation

# ========================================
# INITIALISATION
# ========================================

app = Flask(__name__)
app.config.from_object(Config)

# Créer dossier uploads
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialiser extensions
db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# ========================================
# ROUTES PUBLIQUES
# ========================================

@app.route('/')
def index():
    products = Product.query.filter_by(is_active=True).limit(6).all()
    return render_template('index.html', products=products)

@app.route('/catalog')
def catalog():
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(is_active=True, category=category).all()
    else:
        products = Product.query.filter_by(is_active=True).all()
    return render_template('catalog.html', products=products, selected_category=category)

@app.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template('product_detail.html', product=product)

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
    return render_template('cart.html', items=items, total=total)

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
        session['checkout_info'] = {
            'email': request.form['email'],
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'phone': request.form['phone'],
            'address': request.form['address'],
            'city': request.form['city'],
            'postal_code': request.form['postal_code']
        }
        session.modified = True
    
    items = get_cart_items()
    total = get_cart_total()
    checkout_info = session.get('checkout_info', {})
    
    return render_template('checkout.html', 
                         items=items, 
                         total=total, 
                         checkout_info=checkout_info,
                         paypal_client_id=app.config['PAYPAL_CLIENT_ID'])

@app.route('/payment-success', methods=['POST'])
def payment_success():
    if not session.get('checkout_info') or not get_cart():
        flash('Erreur lors de la validation du paiement', 'danger')
        return redirect(url_for('catalog'))
    
    checkout_info = session['checkout_info']
    order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{Order.query.count() + 1:03d}"
    
    order = Order(
        order_number=order_number,
        customer_email=checkout_info['email'],
        customer_first_name=checkout_info['first_name'],
        customer_last_name=checkout_info['last_name'],
        customer_phone=checkout_info['phone'],
        shipping_address=checkout_info['address'],
        shipping_city=checkout_info['city'],
        shipping_postal_code=checkout_info['postal_code'],
        total_amount=get_cart_total(),
        status='paid'
    )
    
    db.session.add(order)
    db.session.commit()
    
    # Ajouter items
    for item in get_cart_items():
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            quantity=item['quantity'],
            subtotal=item['subtotal']
        )
        db.session.add(order_item)
    db.session.commit()
    
    # ENVOYER EMAIL
    send_order_confirmation(mail, order)
    
    # Vider panier
    session['cart'] = []
    session.pop('checkout_info', None)
    session.modified = True
    
    flash(f'Paiement confirmé ! Commande {order_number} enregistrée.', 'success')
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/order-success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_success.html', order=order)

# ========================================
# ROUTES PAGES LÉGALES
# ========================================

@app.route('/politique-confidentialite')
def privacy_policy():
    return render_template('legal/privacy.html')

@app.route('/conditions-vente')
def terms_of_sale():
    return render_template('legal/terms.html')

@app.route('/mentions-legales')
def legal_notice():
    return render_template('legal/legal_notice.html')

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
    return render_template('admin/login.html')

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
    
    return render_template('admin/dashboard.html', 
                         total_orders=total_orders,
                         total_revenue=total_revenue,
                         pending_orders=pending_orders,
                         total_products=total_products,
                         recent_orders=recent_orders)

@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    if request.method == 'POST':
        image_url = request.form.get('image_url')

        if not image_url:
            flash('Veuillez coller le lien de l’image (ex: https://i.ibb.co/...)', 'danger')
            return redirect(url_for('admin_add_product'))
        
        product = Product(
            name=request.form['name'],
            brand=request.form['brand'],
            description=request.form['description'],
            price=float(request.form['price']),
            stock=int(request.form['stock']),
            category=request.form['category'],
            size_ml=int(request.form['size_ml']),
            image_url=image_url
        )

        db.session.add(product)
        db.session.commit()

        flash(f'Produit {product.name} ajouté avec succès!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=None)

@app.route('/admin/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.brand = request.form['brand']
        product.description = request.form['description']
        product.price = float(request.form['price'])
        product.stock = int(request.form['stock'])
        product.category = request.form['category']
        product.size_ml = int(request.form['size_ml'])
        product.image_url = request.form.get('image_url') or product.image_url

        db.session.commit()
        flash(f'Produit {product.name} modifié avec succès!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=product)


@app.route('/admin/products/delete/<int:id>')
@login_required
def admin_delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Produit {product.name} supprimé', 'info')
    return redirect(url_for('admin_products'))

@app.route('/admin/products/toggle/<int:id>')
@login_required
def admin_toggle_product(id):
    product = Product.query.get_or_404(id)
    product.is_active = not product.is_active
    db.session.commit()
    status = "activé" if product.is_active else "désactivé"
    flash(f'Produit {product.name} {status}', 'info')
    return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/orders/<int:id>/status', methods=['POST'])
@login_required
def admin_update_order_status(id):
    order = Order.query.get_or_404(id)
    order.status = request.form['status']
    db.session.commit()
    flash('Statut mis à jour', 'success')
    return redirect(url_for('admin_orders'))

# ========================================
# INITIALISATION BASE DE DONNÉES
# ========================================

def init_db():
    with app.app_context():
        db.create_all()
        print("✅ Tables créées")
        
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin créé")
        
        if Product.query.count() == 0:
            demo_products = [
                Product(name="Noir Extrême", brand="Tom Ford", description="Parfum oriental boisé intense", price=145.00, stock=15, category="Homme", size_ml=100, image_url="https://images.unsplash.com/photo-1541643600914-78b084683601?w=500"),
                Product(name="La Vie Est Belle", brand="Lancôme", description="Essence du bonheur", price=98.00, stock=20, category="Femme", size_ml=50, image_url="https://images.unsplash.com/photo-1588405748880-12d1d2a59cca?w=500"),
            ]
            for product in demo_products:
                db.session.add(product)
            db.session.commit()
            print("✅ Produits créés")

init_db()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 OPALINE PARFUMS - SERVEUR DÉMARRÉ!")
    print("="*50)
    print("\nSite Public: http://localhost:5000")
    print("Admin Panel: http://localhost:5000/admin/login")
    print("\nUsername: admin")
    print("Password: admin123")
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)