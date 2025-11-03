"""
Script pour migrer l'ancienne base de données vers le nouveau système avec variantes
À exécuter UNE SEULE FOIS après avoir mis à jour models.py
"""

from app import app, db
from models import Product, ProductVariant

def migrate_to_variants():
    """Migre les anciens produits vers le système de variantes"""
    with app.app_context():
        print("🔄 Début de la migration...")
        
        # Récupérer tous les produits existants
        products = Product.query.all()
        
        for product in products:
            # Vérifier si le produit a déjà des variantes
            if product.variants:
                print(f"⚠️  {product.name} a déjà des variantes, passage...")
                continue
            
            # Créer une variante avec les données existantes
            variant = ProductVariant(
                product_id=product.id,
                size_ml=product.size_ml if hasattr(product, 'size_ml') else 50,
                price=product.price if hasattr(product, 'price') else 0,
                stock=product.stock if hasattr(product, 'stock') else 10,
                is_active=True
            )
            
            db.session.add(variant)
            print(f"✅ Variante créée pour {product.name} - {variant.size_ml}ml à ${variant.price}")
        
        # Sauvegarder
        db.session.commit()
        print("✨ Migration terminée avec succès !")

if __name__ == '__main__':
    migrate_to_variants()