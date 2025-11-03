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
    from models import ProductVariant
    cart = get_cart()
    total = 0
    for item in cart:
        variant = ProductVariant.query.get(item['variant_id'])
        if variant:
            total += variant.price * item['quantity']
    return total

def get_cart_items():
    """Récupère les articles du panier avec détails"""
    from models import Product, ProductVariant
    cart = get_cart()
    items = []
    for item in cart:
        variant = ProductVariant.query.get(item['variant_id'])
        if variant:
            product = Product.query.get(variant.product_id)
            items.append({
                'product': product,
                'variant': variant,
                'quantity': item['quantity'],
                'subtotal': variant.price * item['quantity']
            })
    return items