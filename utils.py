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
    from app import db
    from models import ProductVariant
    cart = get_cart()
    total = 0.0

    for item in cart:
        # 🧠 On vérifie que la clé 'variant_id' existe
        variant_id = item.get('variant_id')
        if not variant_id:
            continue

        variant = db.session.get(ProductVariant, variant_id)
        if not variant:
            continue

        quantity = item.get('quantity', 1)
        total += variant.price * quantity

    return total


def get_cart_items():
    """Récupère les articles du panier avec détails"""
    from app import db
    from models import Product, ProductVariant

    cart = get_cart()
    items = []

    for item in cart:
        # 🧠 Vérifie que la clé variant_id existe
        if 'variant_id' not in item:
            continue

        variant = db.session.get(ProductVariant, item['variant_id'])
        if not variant:
            continue

        product = db.session.get(Product, variant.product_id)
        if not product:
            continue

        items.append({
            'product': product,
            'variant': variant,
            'quantity': item.get('quantity', 1),
            'subtotal': variant.price * item.get('quantity', 1)
        })

    return items

