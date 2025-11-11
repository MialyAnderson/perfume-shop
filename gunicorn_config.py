# gunicorn_config.py
bind = "0.0.0.0:10000"
workers = 2
timeout = 120  # 2 minutes au lieu de 30 secondes
```

**Puis modifie le `render.yaml` ou la commande de démarrage sur Render :**

Dans Render Dashboard → ton service → Settings → Build & Deploy → Start Command:

**Change de :**
```
gunicorn app:app
```

**À :**
```
gunicorn -c gunicorn_config.py app:app
```

---

## **❌ PROBLÈME 2 : Édition de produit impossible**
```
ForeignKeyViolation: update or delete on table "product_variant" violates foreign key constraint
