#!/bin/bash

echo "============================================================"
echo "📄 GÉNÉRATION COMPLÈTE DES TEMPLATES - OPALINE PARFUMS"
echo "============================================================"
echo ""

# Créer les dossiers
echo "📁 Création de la structure..."
mkdir -p templates/legal
mkdir -p templates/admin
echo "✅ Structure créée"
echo ""

# ========================================
# 1. BASE.HTML
# ========================================
echo "📝 [1/15] Création de base.html..."
cat > templates/base.html << 'ENDOFFILE'
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
        .btn-outline-primary { color: #000000; border: 1px solid #000000; }
        .btn-outline-primary:hover { background: #000000; color: white; }
        .btn-outline-primary.active { background: #000000; color: white; }
        .hero { background: linear-gradient(135deg, #f5f5f5, #ffffff); padding: 80px 0; }
        .footer { background: #000000; color: white; padding: 40px 0; margin-top: 60px; }
        .star-rating { display: flex; flex-direction: row-reverse; justify-content: flex-end; font-size: 2rem; gap: 5px; }
        .star-rating input[type="radio"] { display: none; }
        .star-rating label { cursor: pointer; color: #ddd; transition: color 0.2s; }
        .star-rating label:hover, .star-rating label:hover ~ label, .star-rating input[type="radio"]:checked ~ label { color: #ffc107; }
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
        <div class="container">
            <div class="row">
                <div class="col-md-4 text-center text-md-start mb-3 mb-md-0">
                    <h5 style="letter-spacing: 2px;">OPALINE PARFUMS</h5>
                    <p>&copy; 2025 Tous droits réservés</p>
                </div>
                <div class="col-md-8 text-center text-md-end">
                    <a href="{{ url_for('privacy_policy') }}" class="text-white text-decoration-none me-3">Confidentialité</a>
                    <a href="{{ url_for('terms_of_sale') }}" class="text-white text-decoration-none me-3">Conditions</a>
                    <a href="{{ url_for('legal_notice') }}" class="text-white text-decoration-none">Mentions légales</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
ENDOFFILE
echo "✅ base.html créé"

# ========================================
# 2. INDEX.HTML
# ========================================
echo "📝 [2/15] Création de index.html..."
cat > templates/index.html << 'ENDOFFILE'
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
                <div class="card-body d-flex flex-column">
                    <h5>{{ product.name }}</h5>
                    <p class="text-muted">{{ product.brand }}</p>
                    <p class="flex-grow-1">{{ product.description[:80] }}...</p>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="h5">${{ "%.2f"|format(product.price) }}</span>
                        <a href="{{ url_for('product_detail', id=product.id) }}" class="btn btn-outline-primary">Voir</a>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    <div class="text-center mt-5">
        <a href="{{ url_for('catalog') }}" class="btn btn-primary btn-lg">Voir Tous les Parfums</a>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ index.html créé"

# ========================================
# 3. CATALOG.HTML
# ========================================
echo "📝 [3/15] Création de catalog.html..."
cat > templates/catalog.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Catalogue - OPALINE PARFUMS{% endblock %}

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
        <div class="col-md-4">
            <div class="card product-card h-100">
                <img src="{{ product.image_url }}" class="card-img-top" alt="{{ product.name }}" style="height: 300px; object-fit: cover;">
                <div class="card-body d-flex flex-column">
                    <h5>{{ product.name }}</h5>
                    <p class="text-muted small">{{ product.brand }}</p>
                    <p class="flex-grow-1">{{ product.description[:100] }}...</p>
                    <div class="mb-2">
                        <span class="badge bg-secondary">{{ product.size_ml }}ml</span>
                        <span class="badge bg-dark">{{ product.category }}</span>
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="h5">${{ "%.2f"|format(product.price) }}</span>
                        <div>
                            <a href="{{ url_for('product_detail', id=product.id) }}" class="btn btn-outline-primary btn-sm me-2"><i class="fas fa-eye"></i></a>
                            <a href="{{ url_for('add_to_cart', product_id=product.id) }}" class="btn btn-primary btn-sm"><i class="fas fa-cart-plus"></i></a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    
    {% if products|length == 0 %}
    <div class="alert alert-info text-center mt-5">
        <i class="fas fa-info-circle"></i> Aucun produit dans cette catégorie.
    </div>
    {% endif %}
</div>
{% endblock %}
ENDOFFILE
echo "✅ catalog.html créé"

# ========================================
# 4. PRODUCT_DETAIL.HTML
# ========================================
echo "📝 [4/15] Création de product_detail.html..."
cat > templates/product_detail.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}{{ product.name }} - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row">
        <div class="col-md-6">
            <img src="{{ product.image_url }}" class="img-fluid rounded" alt="{{ product.name }}">
        </div>
        
        <div class="col-md-6">
            <h1 class="mb-3">{{ product.name }}</h1>
            <h5 class="text-muted mb-4">{{ product.brand }}</h5>
            
            {% if product.reviews %}
            <div class="mb-3">
                {% set avg_rating = (product.reviews|sum(attribute='rating')) / (product.reviews|length) %}
                <span class="text-warning">
                    {% for i in range(5) %}
                        {% if i < avg_rating|round %}
                            <i class="fas fa-star"></i>
                        {% else %}
                            <i class="far fa-star"></i>
                        {% endif %}
                    {% endfor %}
                </span>
                <span class="text-muted ms-2">({{ product.reviews|length }} avis)</span>
            </div>
            {% endif %}
            
            <p class="lead">{{ product.description }}</p>
            
            <div class="my-4">
                <span class="badge bg-secondary me-2"><i class="fas fa-flask"></i> {{ product.size_ml }}ml</span>
                <span class="badge bg-dark"><i class="fas fa-tag"></i> {{ product.category }}</span>
            </div>
            
            <div class="d-flex align-items-center mb-4">
                <h2 class="mb-0 me-4">${{ "%.2f"|format(product.price) }}</h2>
                {% if product.stock > 0 %}
                    <span class="badge bg-success">En stock ({{ product.stock }})</span>
                {% else %}
                    <span class="badge bg-danger">Rupture de stock</span>
                {% endif %}
            </div>
            
            {% if product.stock > 0 %}
            <a href="{{ url_for('add_to_cart', product_id=product.id) }}" class="btn btn-primary btn-lg w-100">
                <i class="fas fa-cart-plus"></i> Ajouter au panier
            </a>
            {% else %}
            <button class="btn btn-secondary btn-lg w-100" disabled>Indisponible</button>
            {% endif %}
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-12">
            <h3 class="mb-4">Avis Clients</h3>
            
            <div class="card mb-4">
                <div class="card-body">
                    <h5 class="card-title">Donnez votre avis</h5>
                    <form method="POST" action="{{ url_for('add_review', id=product.id) }}">
                        <div class="mb-3">
                            <label class="form-label">Votre nom (optionnel)</label>
                            <input type="text" class="form-control" name="author_name" placeholder="Anonyme">
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Note *</label>
                            <div class="star-rating">
                                <input type="radio" name="rating" value="5" id="star5" required>
                                <label for="star5"><i class="fas fa-star"></i></label>
                                
                                <input type="radio" name="rating" value="4" id="star4">
                                <label for="star4"><i class="fas fa-star"></i></label>
                                
                                <input type="radio" name="rating" value="3" id="star3">
                                <label for="star3"><i class="fas fa-star"></i></label>
                                
                                <input type="radio" name="rating" value="2" id="star2">
                                <label for="star2"><i class="fas fa-star"></i></label>
                                
                                <input type="radio" name="rating" value="1" id="star1">
                                <label for="star1"><i class="fas fa-star"></i></label>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Votre commentaire *</label>
                            <textarea class="form-control" name="comment" rows="4" required></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-paper-plane"></i> Publier l'avis
                        </button>
                    </form>
                </div>
            </div>
            
            {% for review in product.reviews|sort(attribute='created_at', reverse=true) %}
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="mb-1">{{ review.author_name }}</h6>
                            <small class="text-muted">{{ review.created_at.strftime('%d/%m/%Y') }}</small>
                        </div>
                        <div class="text-warning">
                            {% for i in range(review.rating) %}
                                <i class="fas fa-star"></i>
                            {% endfor %}
                            {% for i in range(5 - review.rating) %}
                                <i class="far fa-star"></i>
                            {% endfor %}
                        </div>
                    </div>
                    <p class="mb-0">{{ review.comment }}</p>
                </div>
            </div>
            {% endfor %}
            
            {% if product.reviews|length == 0 %}
            <div class="alert alert-info">
                <i class="fas fa-info-circle"></i> Soyez le premier à donner votre avis !
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ product_detail.html créé"

# ========================================
# 5. CART.HTML
# ========================================
echo "📝 [5/15] Création de cart.html..."
cat > templates/cart.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Panier - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <h2 class="mb-4"><i class="fas fa-shopping-cart"></i> Mon Panier</h2>
    
    {% if items %}
    <div class="row">
        <div class="col-lg-8">
            {% for item in items %}
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-md-3">
                            <img src="{{ item.product.image_url }}" class="img-fluid rounded" alt="{{ item.product.name }}">
                        </div>
                        <div class="col-md-5">
                            <h5 class="mb-1">{{ item.product.name }}</h5>
                            <p class="text-muted mb-1">{{ item.product.brand }}</p>
                            <span class="badge bg-secondary">{{ item.product.size_ml }}ml</span>
                        </div>
                        <div class="col-md-2 text-center">
                            <p class="mb-1 text-muted">Prix unitaire</p>
                            <h5>${{ "%.2f"|format(item.product.price) }}</h5>
                        </div>
                        <div class="col-md-2 text-center">
                            <p class="mb-1 text-muted">Quantité</p>
                            <h5>{{ item.quantity }}</h5>
                            <p class="mb-0"><small>Total: ${{ "%.2f"|format(item.subtotal) }}</small></p>
                            <a href="{{ url_for('remove_from_cart', product_id=item.product.id) }}" class="btn btn-sm btn-outline-danger mt-2">
                                <i class="fas fa-trash"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="col-lg-4">
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-receipt"></i> Résumé</h5>
                </div>
                <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                        <span>Sous-total</span>
                        <span>${{ "%.2f"|format(total) }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Livraison</span>
                        <span class="text-success">GRATUITE</span>
                    </div>
                    <hr>
                    <div class="d-flex justify-content-between mb-3">
                        <strong>Total</strong>
                        <strong class="h4 text-primary">${{ "%.2f"|format(total) }} CAD</strong>
                    </div>
                    
                    <a href="{{ url_for('checkout') }}" class="btn btn-primary w-100 btn-lg mb-2">
                        <i class="fas fa-lock"></i> Passer la commande
                    </a>
                    <a href="{{ url_for('catalog') }}" class="btn btn-outline-primary w-100">
                        <i class="fas fa-arrow-left"></i> Continuer mes achats
                    </a>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-body">
                    <h6><i class="fas fa-shield-alt text-success"></i> Paiement sécurisé</h6>
                    <p class="small text-muted mb-0">Vos données sont protégées via PayPal</p>
                </div>
            </div>
        </div>
    </div>
    
    {% else %}
    <div class="text-center py-5">
        <i class="fas fa-shopping-cart fa-5x text-muted mb-4"></i>
        <h3>Votre panier est vide</h3>
        <p class="text-muted mb-4">Découvrez notre collection</p>
        <a href="{{ url_for('catalog') }}" class="btn btn-primary btn-lg">
            <i class="fas fa-search"></i> Explorer le catalogue
        </a>
    </div>
    {% endif %}
</div>
{% endblock %}
ENDOFFILE
echo "✅ cart.html créé"

# ========================================
# 6. CHECKOUT.HTML
# ========================================
echo "📝 [6/15] Création de checkout.html..."
cat > templates/checkout.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Paiement - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <h2 class="mb-4"><i class="fas fa-credit-card"></i> Paiement</h2>
    
    <div class="row">
        <div class="col-lg-7">
            {% if not checkout_info %}
            <div class="card mb-4">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-shipping-fast"></i> Informations de livraison</h5>
                </div>
                <div class="card-body">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6 mb-3">
                                <label class="form-label">Prénom *</label>
                                <input type="text" class="form-control" name="first_name" required>
                            </div>
                            <div class="col-md-6 mb-3">
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
                        
                        <div class="mb-3">
                            <label class="form-label">Adresse *</label>
                            <input type="text" class="form-control" name="address" required>
                        </div>
                        
                        <div class="row">
                            <div class="col-md-8 mb-3">
                                <label class="form-label">Ville *</label>
                                <input type="text" class="form-control" name="city" required>
                            </div>
                            <div class="col-md-4 mb-3">
                                <label class="form-label">Code postal *</label>
                                <input type="text" class="form-control" name="postal_code" required>
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">
                            <i class="fas fa-arrow-right"></i> Continuer vers le paiement
                        </button>
                    </form>
                </div>
            </div>
            {% else %}
            <div class="card mb-4">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0"><i class="fas fa-check-circle"></i> Informations enregistrées</h5>
                </div>
                <div class="card-body">
                    <p><strong>{{ checkout_info.first_name }} {{ checkout_info.last_name }}</strong></p>
                    <p class="mb-1"><i class="fas fa-envelope"></i> {{ checkout_info.email }}</p>
                    <p class="mb-1"><i class="fas fa-phone"></i> {{ checkout_info.phone }}</p>
                    <p class="mb-0"><i class="fas fa-map-marker-alt"></i> {{ checkout_info.address }}, {{ checkout_info.city }}, {{ checkout_info.postal_code }}</p>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fab fa-paypal"></i> Paiement sécurisé</h5>
                </div>
                <div class="card-body">
                    <div id="paypal-button-container"></div>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="col-lg-5">
            <div class="card sticky-top" style="top: 20px;">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-shopping-bag"></i> Votre commande</h5>
                </div>
                <div class="card-body">
                    {% for item in items %}
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom">
                        <div class="d-flex align-items-center">
                            <img src="{{ item.product.image_url }}" class="rounded me-3" style="width: 60px; height: 60px; object-fit: cover;" alt="{{ item.product.name }}">
                            <div>
                                <h6 class="mb-0">{{ item.product.name }}</h6>
                                <small class="text-muted">Qté: {{ item.quantity }}</small>
                            </div>
                        </div>
                        <span>${{ "%.2f"|format(item.subtotal) }}</span>
                    </div>
                    {% endfor %}
                    
                    <div class="d-flex justify-content-between mb-2">
                        <span>Sous-total</span>
                        <span>${{ "%.2f"|format(total) }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Livraison</span>
                        <span class="text-success">GRATUITE</span>
                    </div>
                    <hr>
                    <div class="d-flex justify-content-between">
                        <strong>Total</strong>
                        <strong class="h4 text-primary">${{ "%.2f"|format(total) }} CAD</strong>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

{% if checkout_info %}
<script src="https://www.paypal.com/sdk/js?client-id={{ paypal_client_id }}&currency=CAD"></script>
<script>
    paypal.Buttons({
        createOrder: function(data, actions) {
            return actions.order.create({
                purchase_units: [{
                    amount: {
                        value: '{{ "%.2f"|format(total) }}'
                    }
                }]
            });
        },
        onApprove: function(data, actions) {
            return actions.order.capture().then(function(details) {
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = '{{ url_for("payment_success") }}';
                
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'paypal_order_id';
                input.value = data.orderID;
                
                form.appendChild(input);
                document.body.appendChild(form);
                form.submit();
            });
        },
        onError: function(err) {
            console.error('Erreur PayPal:', err);
            alert('Une erreur est survenue. Veuillez réessayer.');
        }
    }).render('#paypal-button-container');
</script>
{% endif %}
{% endblock %}
ENDOFFILE
echo "✅ checkout.html créé"

# ========================================
# 7. ORDER_SUCCESS.HTML
# ========================================
echo "📝 [7/15] Création de order_success.html..."
cat > templates/order_success.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Commande confirmée - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="text-center mb-5">
                <div class="mb-4">
                    <i class="fas fa-check-circle fa-5x text-success"></i>
                </div>
                <h1 class="mb-3">Commande confirmée !</h1>
                <p class="lead text-muted">Merci pour votre achat.</p>
            </div>
            
            <div class="card mb-4">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-receipt"></i> Détails de votre commande</h5>
                </div>
                <div class="card-body">
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h6 class="text-muted mb-2">Numéro de commande</h6>
                            <h4 class="text-primary">{{ order.order_number }}</h4>
                        </div>
                        <div class="col-md-6 text-md-end">
                            <h6 class="text-muted mb-2">Date</h6>
                            <p class="mb-0">{{ order.created_at.strftime('%d/%m/%Y à %H:%M') }}</p>
                        </div>
                    </div>
                    
                    <h6 class="mb-3">Articles commandés</h6>
                    {% for item in order.items %}
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-3 {% if not loop.last %}border-bottom{% endif %}">
                        <div class="d-flex align-items-center">
                            <img src="{{ item.product.image_url }}" class="rounded me-3" style="width: 80px; height: 80px; object-fit: cover;">
                            <div>
                                <h6 class="mb-1">{{ item.product.name }}</h6>
                                <p class="text-muted small mb-0">{{ item.product.brand }} - {{ item.product.size_ml }}ml</p>
                                <p class="text-muted small mb-0">Quantité: {{ item.quantity }}</p>
                            </div>
                        </div>
                        <div class="text-end">
                            <p class="mb-0">${{ "%.2f"|format(item.product.price) }} × {{ item.quantity }}</p>
                            <p class="mb-0"><strong>${{ "%.2f"|format(item.subtotal) }}</strong></p>
                        </div>
                    </div>
                    {% endfor %}
                    
                    <div class="d-flex justify-content-between align-items-center pt-3 border-top">
                        <h5 class="mb-0">Total payé</h5>
                        <h4 class="mb-0 text-primary">${{ "%.2f"|format(order.total_amount) }} CAD</h4>
                    </div>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header bg-dark text-white">
                    <h5 class="mb-0"><i class="fas fa-shipping-fast"></i> Livraison</h5>
                </div>
                <div class="card-body">
                    <p><strong>{{ order.customer_first_name }} {{ order.customer_last_name }}</strong></p>
                    <p class="mb-0">{{ order.shipping_address }}</p>
                    <p class="mb-0">{{ order.shipping_city }}, {{ order.shipping_postal_code }}</p>
                </div>
            </div>
            
            <div class="alert alert-info">
                <h6><i class="fas fa-info-circle"></i> Prochaines étapes</h6>
                <ul class="mb-0">
                    <li>Email de confirmation envoyé à {{ order.customer_email }}</li>
                    <li>Traitement sous 24-48h</li>
                    <li>Livraison: 3-5 jours ouvrables</li>
                </ul>
            </div>
            
            <div class="text-center">
                <a href="{{ url_for('index') }}" class="btn btn-primary btn-lg me-2">
                    <i class="fas fa-home"></i> Accueil
                </a>
                <a href="{{ url_for('catalog') }}" class="btn btn-outline-primary btn-lg">
                    <i class="fas fa-shopping-bag"></i> Continuer
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ order_success.html créé"

# ========================================
# 8. LEGAL/PRIVACY.HTML
# ========================================
echo "📝 [8/15] Création de legal/privacy.html..."
cat > templates/legal/privacy.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Politique de confidentialité - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <h1 class="mb-4">Politique de confidentialité</h1>
    
    <div class="card">
        <div class="card-body">
            <p class="lead">Dernière mise à jour : Janvier 2025</p>
            
            <h3 class="mt-4">1. Collecte des informations</h3>
            <p>Nous collectons les informations que vous nous fournissez directement lorsque vous :</p>
            <ul>
                <li>Passez une commande</li>
                <li>Créez un compte</li>
                <li>Nous contactez</li>
            </ul>
            
            <h3 class="mt-4">2. Utilisation des informations</h3>
            <p>Les informations collectées sont utilisées pour :</p>
            <ul>
                <li>Traiter vos commandes</li>
                <li>Communiquer avec vous</li>
                <li>Améliorer nos services</li>
            </ul>
            
            <h3 class="mt-4">3. Protection des données</h3>
            <p>Nous mettons en œuvre des mesures de sécurité appropriées pour protéger vos informations personnelles.</p>
            
            <h3 class="mt-4">4. Contact</h3>
            <p><strong>Email :</strong> opaline.parfums@gmail.com</p>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ legal/privacy.html créé"

# ========================================
# 9. LEGAL/TERMS.HTML
# ========================================
echo "📝 [9/15] Création de legal/terms.html..."
cat > templates/legal/terms.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Conditions de vente - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <h1 class="mb-4">Conditions générales de vente</h1>
    
    <div class="card">
        <div class="card-body">
            <p class="lead">Dernière mise à jour : Janvier 2025</p>
            
            <h3 class="mt-4">1. Objet</h3>
            <p>Les présentes conditions régissent les ventes sur OPALINE PARFUMS.</p>
            
            <h3 class="mt-4">2. Prix</h3>
            <p>Les prix sont indiqués en dollars canadiens (CAD) toutes taxes comprises.</p>
            
            <h3 class="mt-4">3. Paiement</h3>
            <p>Le paiement s'effectue via PayPal.</p>
            
            <h3 class="mt-4">4. Livraison</h3>
            <p>Délais : 3 à 5 jours ouvrables</p>
            <ul>
                <li>Livraison gratuite</li>
                <li>Canada uniquement</li>
            </ul>
            
            <h3 class="mt-4">5. Droit de rétractation</h3>
            <p>Vous disposez de 14 jours à compter de la réception.</p>
            
            <h3 class="mt-4">6. Contact</h3>
            <p><strong>Email :</strong> opaline.parfums@gmail.com</p>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ legal/terms.html créé"

# ========================================
# 10. LEGAL/LEGAL_NOTICE.HTML
# ========================================
echo "📝 [10/15] Création de legal/legal_notice.html..."
cat > templates/legal/legal_notice.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Mentions légales - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <h1 class="mb-4">Mentions légales</h1>
    
    <div class="card">
        <div class="card-body">
            <h3 class="mt-4">1. Éditeur du site</h3>
            <p><strong>Raison sociale :</strong> OPALINE PARFUMS</p>
            <p><strong>Email :</strong> opaline.parfums@gmail.com</p>
            <p><strong>Adresse :</strong> [À COMPLÉTER]</p>
            
            <h3 class="mt-4">2. Hébergement</h3>
            <p><strong>Hébergeur :</strong> Render</p>
            <p><strong>Site :</strong> https://render.com</p>
            
            <h3 class="mt-4">3. Propriété intellectuelle</h3>
            <p>L'ensemble du contenu est la propriété de OPALINE PARFUMS.</p>
            
            <h3 class="mt-4">4. Données personnelles</h3>
            <p>Pour exercer vos droits : opaline.parfums@gmail.com</p>
            
            <div class="alert alert-info mt-4">
                <i class="fas fa-info-circle"></i> <strong>Note :</strong> Complétez les informations manquantes.
            </div>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ legal/legal_notice.html créé"

# ========================================
# 11. ADMIN/LOGIN.HTML
# ========================================
echo "📝 [11/15] Création de admin/login.html..."
cat > templates/admin/login.html << 'ENDOFFILE'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connexion Admin - OPALINE PARFUMS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-card {
            max-width: 400px;
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="login-card mx-auto">
            <div class="card">
                <div class="card-body p-5">
                    <div class="text-center mb-4">
                        <i class="fas fa-user-shield fa-3x text-primary mb-3"></i>
                        <h2 class="mb-2">OPALINE PARFUMS</h2>
                        <p class="text-muted">Panneau d'administration</p>
                    </div>
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label"><i class="fas fa-user"></i> Nom d'utilisateur</label>
                            <input type="text" class="form-control form-control-lg" name="username" required autofocus>
                        </div>
                        
                        <div class="mb-4">
                            <label class="form-label"><i class="fas fa-lock"></i> Mot de passe</label>
                            <input type="password" class="form-control form-control-lg" name="password" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary btn-lg w-100 mb-3">
                            <i class="fas fa-sign-in-alt"></i> Se connecter
                        </button>
                        
                        <div class="text-center">
                            <a href="{{ url_for('index') }}" class="text-muted text-decoration-none">
                                <i class="fas fa-arrow-left"></i> Retour au site
                            </a>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="text-center mt-3 text-white">
                <small><i class="fas fa-info-circle"></i> Identifiants: admin / admin123</small>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
ENDOFFILE
echo "✅ admin/login.html créé"

# ========================================
# 12. ADMIN/DASHBOARD.HTML
# ========================================
echo "📝 [12/15] Création de admin/dashboard.html..."
cat > templates/admin/dashboard.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Tableau de bord Admin - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fas fa-chart-line"></i> Tableau de bord</h2>
        <a href="{{ url_for('admin_logout') }}" class="btn btn-outline-danger">
            <i class="fas fa-sign-out-alt"></i> Déconnexion
        </a>
    </div>
    
    <div class="row g-4 mb-5">
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">Commandes totales</h6>
                            <h2 class="mb-0">{{ total_orders }}</h2>
                        </div>
                        <i class="fas fa-shopping-bag fa-3x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">Revenus totaux</h6>
                            <h2 class="mb-0">${{ "%.2f"|format(total_revenue) }}</h2>
                        </div>
                        <i class="fas fa-dollar-sign fa-3x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">En attente</h6>
                            <h2 class="mb-0">{{ pending_orders }}</h2>
                        </div>
                        <i class="fas fa-clock fa-3x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card bg-info text-white">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">Produits</h6>
                            <h2 class="mb-0">{{ total_products }}</h2>
                        </div>
                        <i class="fas fa-box fa-3x opacity-50"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row g-4 mb-5">
        <div class="col-md-6">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-boxes fa-4x text-primary mb-3"></i>
                    <h4>Gestion des Produits</h4>
                    <p class="text-muted">Ajouter, modifier ou supprimer</p>
                    <a href="{{ url_for('admin_products') }}" class="btn btn-primary">
                        <i class="fas fa-arrow-right"></i> Gérer
                    </a>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card h-100">
                <div class="card-body text-center">
                    <i class="fas fa-list-alt fa-4x text-success mb-3"></i>
                    <h4>Gestion des Commandes</h4>
                    <p class="text-muted">Voir et gérer les commandes</p>
                    <a href="{{ url_for('admin_orders') }}" class="btn btn-success">
                        <i class="fas fa-arrow-right"></i> Voir
                    </a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <div class="card-header bg-dark text-white">
            <h5 class="mb-0"><i class="fas fa-clock"></i> Commandes récentes</h5>
        </div>
        <div class="card-body">
            {% if recent_orders %}
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>N° Commande</th>
                            <th>Client</th>
                            <th>Montant</th>
                            <th>Statut</th>
                            <th>Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in recent_orders %}
                        <tr>
                            <td><strong>{{ order.order_number }}</strong></td>
                            <td>{{ order.customer_first_name }} {{ order.customer_last_name }}</td>
                            <td>${{ "%.2f"|format(order.total_amount) }}</td>
                            <td>
                                {% if order.status == 'paid' %}
                                    <span class="badge bg-success">Payé</span>
                                {% else %}
                                    <span class="badge bg-warning">{{ order.status }}</span>
                                {% endif %}
                            </td>
                            <td>{{ order.created_at.strftime('%d/%m/%Y') }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <p class="text-center text-muted mb-0">Aucune commande</p>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ admin/dashboard.html créé"

# ========================================
# 13. ADMIN/PRODUCTS.HTML
# ========================================
echo "📝 [13/15] Création de admin/products.html..."
cat > templates/admin/products.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Gestion des Produits - OPALINE PARFUMS{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fas fa-boxes"></i> Gestion des Produits</h2>
        <div>
            <a href="{{ url_for('admin_dashboard') }}" class="btn btn-outline-secondary me-2">
                <i class="fas fa-arrow-left"></i> Retour
            </a>
            <a href="{{ url_for('admin_add_product') }}" class="btn btn-primary">
                <i class="fas fa-plus"></i> Ajouter
            </a>
        </div>
    </div>
    
    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Image</th>
                            <th>Nom</th>
                            <th>Prix</th>
                            <th>Stock</th>
                            <th>Statut</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in products %}
                        <tr>
                            <td>
                                <img src="{{ product.image_url }}" class="rounded" style="width: 60px; height: 60px; object-fit: cover;">
                            </td>
                            <td>
                                <strong>{{ product.name }}</strong>
                                <br><small class="text-muted">{{ product.brand }}</small>
                            </td>
                            <td><strong>${{ "%.2f"|format(product.price) }}</strong></td>
                            <td>
                                {% if product.stock > 10 %}
                                    <span class="badge bg-success">{{ product.stock }}</span>
                                {% elif product.stock > 0 %}
                                    <span class="badge bg-warning">{{ product.stock }}</span>
                                {% else %}
                                    <span class="badge bg-danger">{{ product.stock }}</span>
                                {% endif %}
                            </td>
                            <td>
                                {% if product.is_active %}
                                    <span class="badge bg-success">Actif</span>
                                {% else %}
                                    <span class="badge bg-danger">Inactif</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="{{ url_for('admin_edit_product', id=product.id) }}" class="btn btn-sm btn-primary">
                                    <i class="fas fa-edit"></i>
                                </a>
                                <a href="{{ url_for('admin_toggle_product', id=product.id) }}" class="btn btn-sm btn-warning">
                                    <i class="fas fa-power-off"></i>
                                </a>
                                <a href="{{ url_for('admin_delete_product', id=product.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('Supprimer ?')">
                                    <i class="fas fa-trash"></i>
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if products|length == 0 %}
            <div class="text-center py-5">
                <i class="fas fa-box-open fa-5x text-muted mb-3"></i>
                <h4>Aucun produit</h4>
                <a href="{{ url_for('admin_add_product') }}" class="btn btn-primary">
                    <i class="fas fa-plus"></i> Ajouter
                </a>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ admin/products.html créé"

# ========================================
# 14. ADMIN/PRODUCT_FORM.HTML
# ========================================
echo "📝 [14/15] Création de admin/product_form.html..."
cat > templates/admin/product_form.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}{% if product %}Modifier{% else %}Ajouter{% endif %} un produit{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>
            <i class="fas fa-{% if product %}edit{% else %}plus{% endif %}"></i>
            {% if product %}Modifier{% else %}Ajouter{% endif %} un produit
        </h2>
        <a href="{{ url_for('admin_products') }}" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-left"></i> Retour
        </a>
    </div>
    
    <div class="card">
        <div class="card-body">
            <form method="POST" enctype="multipart/form-data">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Nom *</label>
                        <input type="text" class="form-control" name="name" value="{{ product.name if product else '' }}" required>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Marque *</label>
                        <input type="text" class="form-control" name="brand" value="{{ product.brand if product else '' }}" required>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Description *</label>
                    <textarea class="form-control" name="description" rows="4" required>{{ product.description if product else '' }}</textarea>
                </div>
                
                <div class="row">
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Prix ($) *</label>
                        <input type="number" step="0.01" class="form-control" name="price" value="{{ product.price if product else '' }}" required>
                    </div>
                    
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Stock *</label>
                        <input type="number" class="form-control" name="stock" value="{{ product.stock if product else '10' }}" required>
                    </div>
                    
                    <div class="col-md-4 mb-3">
                        <label class="form-label">Taille (ml) *</label>
                        <select class="form-select" name="size_ml" required>
                            <option value="30" {% if product and product.size_ml == 30 %}selected{% endif %}>30ml</option>
                            <option value="50" {% if product and product.size_ml == 50 %}selected{% elif not product %}selected{% endif %}>50ml</option>
                            <option value="100" {% if product and product.size_ml == 100 %}selected{% endif %}>100ml</option>
                            <option value="150" {% if product and product.size_ml == 150 %}selected{% endif %}>150ml</option>
                        </select>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Catégorie *</label>
                        <select class="form-select" name="category" required>
                            <option value="Homme" {% if product and product.category == 'Homme' %}selected{% endif %}>Homme</option>
                            <option value="Femme" {% if product and product.category == 'Femme' %}selected{% endif %}>Femme</option>
                            <option value="Unisexe" {% if product and product.category == 'Unisexe' %}selected{% endif %}>Unisexe</option>
                        </select>
                    </div>
                    
                    <div class="col-md-6 mb-3">
                        <label class="form-label">Image {% if not product %}*{% endif %}</label>
                        <input type="file" class="form-control" name="image" accept="image/*" {% if not product %}required{% endif %}>
                        {% if product and product.image_url %}
                        <div class="mt-2">
                            <img src="{{ product.image_url }}" class="rounded" style="width: 100px; height: 100px; object-fit: cover;">
                            <p class="small text-muted mb-0">Image actuelle</p>
                        </div>
                        {% endif %}
                    </div>
                </div>
                
                <div class="d-flex gap-2">
                    <button type="submit" class="btn btn-primary btn-lg">
                        <i class="fas fa-save"></i> {% if product %}Modifier{% else %}Ajouter{% endif %}
                    </button>
                    <a href="{{ url_for('admin_products') }}" class="btn btn-outline-secondary btn-lg">
                        <i class="fas fa-times"></i> Annuler
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ admin/product_form.html créé"

# ========================================
# 15. ADMIN/ORDERS.HTML
# ========================================
echo "📝 [15/15] Création de admin/orders.html..."
cat > templates/admin/orders.html << 'ENDOFFILE'
{% extends "base.html" %}

{% block title %}Gestion des Commandes{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2><i class="fas fa-shopping-bag"></i> Gestion des Commandes</h2>
        <a href="{{ url_for('admin_dashboard') }}" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-left"></i> Retour
        </a>
    </div>
    
    <div class="card">
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>N° Commande</th>
                            <th>Client</th>
                            <th>Total</th>
                            <th>Statut</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for order in orders %}
                        <tr>
                            <td><strong>{{ order.order_number }}</strong></td>
                            <td>{{ order.customer_first_name }} {{ order.customer_last_name }}</td>
                            <td><strong>${{ "%.2f"|format(order.total_amount) }}</strong></td>
                            <td>
                                <form method="POST" action="{{ url_for('admin_update_order_status', id=order.id) }}" class="d-inline">
                                    <select name="status" class="form-select form-select-sm" onchange="this.form.submit()">
                                        <option value="pending" {% if order.status == 'pending' %}selected{% endif %}>En attente</option>
                                        <option value="paid" {% if order.status == 'paid' %}selected{% endif %}>Payé</option>
                                        <option value="processing" {% if order.status == 'processing' %}selected{% endif %}>Traitement</option>
                                        <option value="shipped" {% if order.status == 'shipped' %}selected{% endif %}>Expédié</option>
                                        <option value="delivered" {% if order.status == 'delivered' %}selected{% endif %}>Livré</option>
                                        <option value="cancelled" {% if order.status == 'cancelled' %}selected{% endif %}>Annulé</option>
                                    </select>
                                </form>
                            </td>
                            <td>{{ order.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                            <td>
                                <button type="button" class="btn btn-sm btn-info" data-bs-toggle="modal" data-bs-target="#orderModal{{ order.id }}">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </td>
                        </tr>
                        
                        <div class="modal fade" id="orderModal{{ order.id }}" tabindex="-1">
                            <div class="modal-dialog modal-lg">
                                <div class="modal-content">
                                    <div class="modal-header bg-dark text-white">
                                        <h5 class="modal-title">Commande {{ order.order_number }}</h5>
                                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                    </div>
                                    <div class="modal-body">
                                        <h6>Client</h6>
                                        <p>{{ order.customer_first_name }} {{ order.customer_last_name }}</p>
                                        <p>{{ order.customer_email }} | {{ order.customer_phone }}</p>
                                        <p>{{ order.shipping_address }}, {{ order.shipping_city }}, {{ order.shipping_postal_code }}</p>
                                        
                                        <h6 class="mt-4">Articles</h6>
                                        <table class="table table-sm">
                                            <thead>
                                                <tr>
                                                    <th>Produit</th>
                                                    <th>Qté</th>
                                                    <th>Prix</th>
                                                    <th>Total</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {% for item in order.items %}
                                                <tr>
                                                    <td>{{ item.product.name }}</td>
                                                    <td>{{ item.quantity }}</td>
                                                    <td>${{ "%.2f"|format(item.product.price) }}</td>
                                                    <td>${{ "%.2f"|format(item.subtotal) }}</td>
                                                </tr>
                                                {% endfor %}
                                            </tbody>
                                            <tfoot>
                                                <tr class="table-active">
                                                    <td colspan="3" class="text-end"><strong>TOTAL:</strong></td>
                                                    <td><strong>${{ "%.2f"|format(order.total_amount) }}</strong></td>
                                                </tr>
                                            </tfoot>
                                        </table>
                                    </div>
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Fermer</button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            {% if orders|length == 0 %}
            <div class="text-center py-5">
                <i class="fas fa-shopping-bag fa-5x text-muted mb-3"></i>
                <h4>Aucune commande</h4>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
ENDOFFILE
echo "✅ admin/orders.html créé"

echo ""
echo "============================================================"
echo "🎉 GÉNÉRATION COMPLÈTE TERMINÉE !"
echo "============================================================"
echo ""
echo "📊 RÉSUMÉ :"
echo ""
echo "📁 Structure créée :"
echo "   templates/"
echo "   ├── legal/"
echo "   └── admin/"
echo ""
echo "📄 Templates créés : 15/15"
echo ""
echo "   ✅ Templates publics (7) :"
echo "      • base.html"
echo "      • index.html"
echo "      • catalog.html"
echo "      • product_detail.html"
echo "      • cart.html"
echo "      • checkout.html"
echo "      • order_success.html"
echo ""
echo "   ✅ Templates légaux (3) :"
echo "      • legal/privacy.html"
echo "      • legal/terms.html"
echo "      • legal/legal_notice.html"
echo ""
echo "   ✅ Templates admin (5) :"
echo "      • admin/login.html"
echo "      • admin/dashboard.html"
echo "      • admin/products.html"
echo "      • admin/product_form.html"
echo "      • admin/orders.html"
echo ""
echo "============================================================"
echo "✅ TOUS VOS TEMPLATES SONT PRÊTS !"
echo "============================================================"
echo ""
echo "🚀 PROCHAINES ÉTAPES :"
echo ""
echo "1. Copiez le dossier templates/ dans votre projet"
echo "2. Vérifiez que app.py utilise render_template"
echo "3. Testez : python app.py"
echo "4. Ouvrez : http://localhost:5000"
echo ""
echo "✨ Bon développement avec OPALINE PARFUMS !"
echo "============================================================"