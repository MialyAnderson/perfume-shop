from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from flask_session import Session  # ✅ AJOUTE CECI
from config import Config, ALLOWED_EXTENSIONS
from models import db, Admin, Product, Order, OrderItem, Review, ProductVariant, ContactMessage
from utils import get_cart, get_cart_total, get_cart_items, save_uploaded_file
from email_service import send_order_confirmation_resend

app = Flask(__name__)
app.config.from_object(Config)

# ✅ CONFIGURATION SÉCURISÉE POUR RENDER
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "ma_cle_locale_secrete")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)  # initialise la session côté serveur

# ✅ Crée le dossier d’upload s’il n’existe pas
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

migrate = Migrate(app, db)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.context_processor
def utility_processor():
    """Fonctions utilitaires disponibles dans tous les templates"""
    def get_unread_messages_count():
        from models import ContactMessage
        return ContactMessage.query.filter_by(is_read=False).count()
    return dict(get_unread_messages_count=get_unread_messages_count)

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

@app.route('/add-to-cart/<int:variant_id>')
def add_to_cart(variant_id):
    from models import ProductVariant, Product
    from utils import get_cart

    quantity = int(request.args.get('quantity', 1))
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # 🔒 Récupération du panier (et validation de sa structure)
    cart = get_cart()
    if not isinstance(cart, list):
        cart = []
        session['cart'] = cart

    variant = db.session.get(ProductVariant, variant_id)
    if not variant:
        if is_ajax:
            return {"error": "Produit introuvable"}, 404
        flash("Produit introuvable", "danger")
        return redirect(request.referrer or url_for('catalog'))

    product = db.session.get(Product, variant.product_id)
    if not product:
        if is_ajax:
            return {"error": "Produit associé introuvable"}, 404
        flash("Produit associé introuvable", "danger")
        return redirect(request.referrer or url_for('catalog'))

    # ⚙️ Vérifie le stock
    if variant.stock <= 0:
        if is_ajax:
            return {"error": "Rupture de stock"}, 400
        flash(f"{product.name} ({variant.size_ml}ml) est en rupture de stock", "warning")
        return redirect(request.referrer or url_for('catalog'))

    # 🧠 Vérifie que chaque item du panier contient bien les bonnes clés
    for item in cart:
        if not isinstance(item, dict) or 'variant_id' not in item or 'quantity' not in item:
            continue  # Ignore toute donnée corrompue

        if item['variant_id'] == variant_id:
            new_qty = item['quantity'] + quantity
            if new_qty > variant.stock:
                if is_ajax:
                    return {"error": "Stock insuffisant"}, 400
                flash(f"Stock insuffisant pour {product.name} ({variant.size_ml}ml)", "warning")
                return redirect(request.referrer or url_for('catalog'))
            item['quantity'] = new_qty
            session.modified = True
            break
    else:
        # 🛒 Ajout propre si l'article n'existe pas encore
        cart.append({'variant_id': variant_id, 'quantity': quantity})
        session['cart'] = cart
        session.modified = True

    # ✅ Réponse AJAX légère si c’est un ajout via fetch()
    if is_ajax:
        return {"message": f"{product.name} ({variant.size_ml}ml) ajouté au panier", "success": True}, 200

    # ✅ Redirection normale sinon
    flash(f"{product.name} ({variant.size_ml}ml) ajouté au panier!", "success")
    return redirect(request.referrer or url_for('catalog'))


@app.route("/clear-cart")
def clear_cart():
    session.pop('cart', None)
    flash("Panier vidé.", "info")
    return redirect(url_for('view_cart'))



@app.route('/remove-from-cart/<int:variant_id>')
def remove_from_cart(variant_id):
    cart = get_cart()
    cart[:] = [item for item in cart if item['variant_id'] != variant_id]
    session.modified = True
    flash('Produit retiré du panier', 'info')
    return redirect(url_for('view_cart'))

@app.route('/cart/increase/<int:variant_id>')
def increase_quantity(variant_id):
    """Augmente la quantité d'une variante dans le panier"""
    from models import ProductVariant, Product
    
    variant = ProductVariant.query.get_or_404(variant_id)
    product = Product.query.get(variant.product_id)
    cart = get_cart()
    
    for item in cart:
        if item['variant_id'] == variant_id:
            if item['quantity'] < variant.stock:
                item['quantity'] += 1
                session.modified = True
                flash(f'Quantité augmentée pour {product.name} ({variant.size_ml}ml)', 'success')
            else:
                flash(f'Stock insuffisant. Disponible : {variant.stock}', 'warning')
            return redirect(url_for('view_cart'))
    
    flash('Produit non trouvé dans le panier', 'error')
    return redirect(url_for('view_cart'))


@app.route('/cart/decrease/<int:variant_id>')
def decrease_quantity(variant_id):
    """Diminue la quantité d'une variante dans le panier"""
    from models import ProductVariant, Product
    
    variant = ProductVariant.query.get_or_404(variant_id)
    product = Product.query.get(variant.product_id)
    cart = get_cart()
    
    for item in cart:
        if item['variant_id'] == variant_id:
            if item['quantity'] > 1:
                item['quantity'] -= 1
                session.modified = True
                flash(f'Quantité diminuée pour {product.name} ({variant.size_ml}ml)', 'info')
            else:
                cart[:] = [i for i in cart if i['variant_id'] != variant_id]
                session.modified = True
                flash(f'{product.name} ({variant.size_ml}ml) retiré du panier', 'info')
            return redirect(url_for('view_cart'))
    
    flash('Produit non trouvé dans le panier', 'error')
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

    # ✅ CORRECTION : Ajouter variant_id
    for item in get_cart_items():
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            variant_id=item['variant'].id,  # ⭐ AJOUTÉ
            quantity=item['quantity'],
            subtotal=item['subtotal']
        )
        db.session.add(order_item)
    
    db.session.commit()

    send_order_confirmation_resend(order) 

    session['cart'] = []
    session.pop('checkout_info', None)
    session.modified = True
    
    flash(f'Paiement confirmé ! Commande {order_number} enregistrée.', 'success')
    return redirect(url_for('order_success', order_number=order_number))

@app.route('/order-success/<order_number>')
def order_success(order_number):
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template('order_success.html', order=order)

@app.route('/politique-confidentialite')
def privacy_policy():
    return render_template('legal/privacy.html')

@app.route('/conditions-vente')
def terms_of_sale():
    return render_template('legal/terms.html')

@app.route('/mentions-legales')
def legal_notice():
    return render_template('legal/legal_notice.html')

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
            flash('Veuillez coller le lien de l\'image', 'danger') 
            return redirect(url_for('admin_add_product'))
        
        # Créer le produit
        product = Product(
            name=request.form['name'],
            brand=request.form['brand'],
            description=request.form['description'],
            category=request.form['category'],
            image_url=image_url
        )
        
        db.session.add(product)
        db.session.flush()  # Pour obtenir l'ID du produit
        
        # Créer les variantes (tailles)
        variant_sizes = request.form.getlist('variant_size[]')
        variant_prices = request.form.getlist('variant_price[]')
        variant_stocks = request.form.getlist('variant_stock[]')
        
        for size, price, stock in zip(variant_sizes, variant_prices, variant_stocks):
            if size and price:  # Vérifier que les champs ne sont pas vides
                variant = ProductVariant(
                    product_id=product.id,
                    size_ml=int(size),
                    price=float(price),
                    stock=int(stock) if stock else 10
                )
                db.session.add(variant)
        
        db.session.commit()
        flash(f'Produit {product.name} ajouté avec {len(variant_sizes)} variantes!', 'success')
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
        product.category = request.form['category']
        product.image_url = request.form.get('image_url') or product.image_url
        
        # Récupérer les données du formulaire
        variant_sizes = request.form.getlist('variant_size[]')
        variant_prices = request.form.getlist('variant_price[]')
        variant_stocks = request.form.getlist('variant_stock[]')
        
        # ✅ NOUVEAU : Ne supprimer QUE les variantes non utilisées dans des commandes
        existing_variants = ProductVariant.query.filter_by(product_id=product.id).all()
        
        for variant in existing_variants:
            # Vérifier si la variante est dans une commande
            is_in_order = db.session.query(OrderItem).filter_by(variant_id=variant.id).first()
            
            if not is_in_order:
                # Pas dans une commande, on peut supprimer
                db.session.delete(variant)
            else:
                # Dans une commande, on la désactive juste
                variant.is_active = False
        
        # Ajouter/mettre à jour les variantes
        for size, price, stock in zip(variant_sizes, variant_prices, variant_stocks):
            if size and price:
                # Chercher si une variante existe déjà pour cette taille
                existing = ProductVariant.query.filter_by(
                    product_id=product.id,
                    size_ml=int(size)
                ).first()
                
                if existing:
                    # Mettre à jour
                    existing.price = float(price)
                    existing.stock = int(stock) if stock else 10
                    existing.is_active = True
                else:
                    # Créer nouvelle variante
                    variant = ProductVariant(
                        product_id=product.id,
                        size_ml=int(size),
                        price=float(price),
                        stock=int(stock) if stock else 10,
                        is_active=True
                    )
                    db.session.add(variant)
        
        db.session.commit()
        flash(f'Produit {product.name} modifié avec succès!', 'success')
        return redirect(url_for('admin_products'))

    return render_template('admin/product_form.html', product=product)
@app.route('/admin/products/delete/<int:id>')
@login_required
def admin_delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)  # Les variantes seront supprimées automatiquement (cascade)
    db.session.commit()
    flash(f'Produit {product.name} supprimé', 'success')
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

@app.route('/contact', methods=['POST'])
def submit_contact():
    """Soumet un message de contact"""
    try:
        message = ContactMessage(
            name=request.form['name'],
            email=request.form['email'],
            message=request.form['message']
        )
        db.session.add(message)
        db.session.commit()
        
        flash('Merci ! Votre message a été envoyé avec succès.', 'success')
    except Exception as e:
        flash('Erreur lors de l\'envoi du message.', 'danger')
        print(f"Erreur contact: {e}")
    
    return redirect(request.referrer or url_for('index'))


@app.route('/admin/messages')
@login_required
def admin_messages():
    """Liste des messages de contact"""
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    unread_count = ContactMessage.query.filter_by(is_read=False).count()
    return render_template('admin/messages.html', messages=messages, unread_count=unread_count)


@app.route('/admin/messages/<int:id>/read')
@login_required
def admin_mark_read(id):
    """Marquer un message comme lu"""
    message = ContactMessage.query.get_or_404(id)
    message.is_read = True
    db.session.commit()
    flash('Message marqué comme lu', 'success')
    return redirect(url_for('admin_messages'))


@app.route('/admin/messages/<int:id>/delete')
@login_required
def admin_delete_message(id):
    """Supprimer un message"""
    message = ContactMessage.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Message supprimé', 'success')
    return redirect(url_for('admin_messages'))

def init_db():
    with app.app_context():
        db.create_all()
        
        # Créer un compte admin par défaut
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Compte admin créé (username: admin, password: admin123)")

init_db()

if __name__ == '__main__':
    print("\nSite Public: http://localhost:5000")
    print("Admin Panel: http://localhost:5000/admin/login")
    print("\nUsername: admin")
    print("Password: admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)