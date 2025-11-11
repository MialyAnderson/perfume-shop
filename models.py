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
    """Produit (parfum) - Sans prix ni stock car géré par variantes"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    image_url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    
    # Relation avec les variantes
    variants = db.relationship('ProductVariant', backref='product', lazy=True, cascade='all, delete-orphan')
    
    @property
    def min_price(self):
        """Prix minimum parmi toutes les variantes"""
        if self.variants:
            return min(v.price for v in self.variants)
        return 0
    
    @property
    def max_price(self):
        """Prix maximum parmi toutes les variantes"""
        if self.variants:
            return max(v.price for v in self.variants)
        return 0
    
    @property
    def total_stock(self):
        """Stock total de toutes les variantes"""
        if self.variants:
            return sum(v.stock for v in self.variants)
        return 0


class ProductVariant(db.Model):
    """Variante de produit (taille spécifique avec son prix et stock)"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    size_ml = db.Column(db.Integer, nullable=False)  # 3, 5, 10, 30, 50, 100, etc.
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<ProductVariant {self.size_ml}ml - ${self.price}>'


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
    """Article d'une commande - LIÉ À UNE VARIANTE"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    variant_id = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)  # NOUVEAU
    quantity = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')
    variant = db.relationship('ProductVariant')  # NOUVEAU

class ContactMessage(db.Model):
    """Messages de contact des visiteurs"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage {self.name} - {self.email}>'