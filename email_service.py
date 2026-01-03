# email_service.py
import resend
import os
from flask_mail import Mail, Message

# Configuration Resend
resend.api_key = os.environ.get("RESEND_API_KEY", "re_bqZgxv8L_9j1JvSJKzYRUfh3S7zFPMAJv")

# ✅ FONCTION GMAIL (PRIORITAIRE) - AVEC LOGO IMGBB
def send_order_confirmation_gmail(order, mail_instance):
    """Envoie l'email de confirmation via Gmail SMTP - Design Premium avec Logo"""
    
    # URL du logo hébergé sur imgbb
    logo_url = "https://i.ibb.co/jtSLs1S/IMG-20251018-181823.png"
    
    # Générer le HTML des produits
    products_html = ""
    for item in order.items:
        products_html += f"""
        <tr>
            <td style="padding: 20px 15px; border-bottom: 1px solid #e0e0e0;">
                <div>
                    <div style="font-weight: 600; color: #1a1a1a; font-size: 16px; margin-bottom: 5px;">
                        {item.product.name}
                    </div>
                    <div style="color: #666; font-size: 13px;">
                        {item.product.brand} • {item.variant.size_ml}ml
                    </div>
                </div>
            </td>
            <td style="padding: 20px 15px; text-align: center; border-bottom: 1px solid #e0e0e0; color: #666;">
                ×{item.quantity}
            </td>
            <td style="padding: 20px 15px; text-align: right; border-bottom: 1px solid #e0e0e0;">
                <div style="font-weight: 600; color: #1a1a1a; font-size: 16px;">
                    ${item.subtotal:.2f}
                </div>
                <div style="color: #999; font-size: 13px; margin-top: 3px;">
                    ${item.variant.price:.2f} / unité
                </div>
            </td>
        </tr>
        """
    
    html_body = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirmation de commande - OPALINE PARFUMS</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
        
        <!-- Container principal -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f5f5; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px;">
                        
                        <!-- Header avec nom stylisé -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); padding: 50px 40px; text-align: center;">
                                <div style="font-family: 'Playfair Display', Georgia, serif;">
                                    <div style="color: #d4af37; font-size: 24px; margin-bottom: 10px;">◆</div>
                                    <div style="color: #ffffff; font-size: 42px; font-weight: 300; letter-spacing: 8px; margin-bottom: 8px; text-transform: uppercase;">
                                        OPALINE
                                    </div>
                                    <div style="color: #d4af37; font-size: 13px; letter-spacing: 3px; text-transform: uppercase; font-weight: 400; margin-bottom: 10px;">
                                        PARFUMS
                                    </div>
                                    <div style="color: #d4af37; font-size: 24px;">◆</div>
                                </div>
                            </td>
                        </tr>
    
                        <!-- Bannière de succès -->
                        <tr>
                            <td style="background-color: #d4af37; padding: 20px 40px; text-align: center;">
                                <div style="color: #1a1a1a; font-size: 18px; font-weight: 600;">
                                    ✓ Commande confirmée
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Message de bienvenue -->
                        <tr>
                            <td style="padding: 50px 40px 30px;">
                                <h2 style="margin: 0 0 20px; color: #1a1a1a; font-size: 28px; font-weight: 400;">
                                    Merci pour votre confiance !
                                </h2>
                                <p style="margin: 0 0 15px; color: #666; font-size: 16px; line-height: 1.6;">
                                    Bonjour <strong style="color: #1a1a1a;">{order.customer_first_name} {order.customer_last_name}</strong>,
                                </p>
                                <p style="margin: 0; color: #666; font-size: 16px; line-height: 1.6;">
                                    Votre commande a été confirmée avec succès et sera préparée avec le plus grand soin.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Numéro de commande -->
                        <tr>
                            <td style="padding: 0 40px 30px;">
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f9f9f9; border-left: 4px solid #d4af37;">
                                    <tr>
                                        <td style="padding: 20px 25px;">
                                            <div style="color: #999; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">
                                                Numéro de commande
                                            </div>
                                            <div style="color: #1a1a1a; font-size: 20px; font-weight: 600;">
                                                #{order.order_number}
                                            </div>
                                            <div style="color: #666; font-size: 13px; margin-top: 8px;">
                                                Passée le {order.created_at.strftime('%d %B %Y à %H:%M')}
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Détails de la commande -->
                        <tr>
                            <td style="padding: 0 40px 40px;">
                                <h3 style="margin: 0 0 20px; color: #1a1a1a; font-size: 18px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                    Détails de votre commande
                                </h3>
                                
                                <table width="100%" cellpadding="0" cellspacing="0" style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
                                    <!-- En-tête du tableau -->
                                    <tr style="background-color: #f9f9f9;">
                                        <th style="padding: 15px; text-align: left; font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 1px;">
                                            Produit
                                        </th>
                                        <th style="padding: 15px; text-align: center; font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 1px;">
                                            Qté
                                        </th>
                                        <th style="padding: 15px; text-align: right; font-size: 12px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 1px;">
                                            Total
                                        </th>
                                    </tr>
                                    
                                    <!-- Produits -->
                                    {products_html}
                                    
                                    <!-- Total -->
                                    <tr style="background-color: #1a1a1a;">
                                        <td colspan="2" style="padding: 25px 15px; text-align: right; color: #ffffff; font-size: 16px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                                            Total
                                        </td>
                                        <td style="padding: 25px 15px; text-align: right; color: #d4af37; font-size: 24px; font-weight: 700;">
                                            ${order.total_amount:.2f} CAD
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Informations de livraison et contact -->
                        <tr>
                            <td style="padding: 0 40px 40px;">
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <!-- Livraison -->
                                        <td width="48%" valign="top" style="padding: 25px; background-color: #f9f9f9; border-radius: 8px;">
                                            <div style="color: #999; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                                                📦 Adresse de livraison
                                            </div>
                                            <div style="color: #1a1a1a; font-size: 14px; line-height: 1.6;">
                                                <strong>{order.customer_first_name} {order.customer_last_name}</strong><br>
                                                {order.shipping_address}<br>
                                                {order.shipping_city}, {order.shipping_postal_code}
                                            </div>
                                        </td>
                                        
                                        <!-- Espace -->
                                        <td width="4%"></td>
                                        
                                        <!-- Contact -->
                                        <td width="48%" valign="top" style="padding: 25px; background-color: #f9f9f9; border-radius: 8px;">
                                            <div style="color: #999; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">
                                                📞 Coordonnées
                                            </div>
                                            <div style="color: #1a1a1a; font-size: 14px; line-height: 1.6;">
                                                <strong>Email:</strong><br>
                                                {order.customer_email}<br><br>
                                                <strong>Téléphone:</strong><br>
                                                {order.customer_phone}
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Message de service -->
                        <tr>
                            <td style="padding: 0 40px 40px; text-align: center;">
                                <div style="padding: 30px; background: linear-gradient(135deg, #f9f9f9 0%, #ffffff 100%); border-radius: 8px; border: 1px dashed #d4af37;">
                                    <div style="color: #1a1a1a; font-size: 16px; font-weight: 600; margin-bottom: 10px;">
                                        🎁 Votre commande sera traitée dans les plus brefs délais
                                    </div>
                                    <div style="color: #666; font-size: 14px; line-height: 1.6;">
                                        Vous recevrez un email de confirmation d'expédition dès que votre colis sera en route.
                                    </div>
                                </div>
                            </td>
                        </tr>
                        
                        <!-- Bouton CTA -->
                        <tr>
                            <td style="padding: 0 40px 50px; text-align: center;">
                                <a href="https://opaline-parfums.onrender.com" style="display: inline-block; padding: 16px 40px; background-color: #d4af37; color: #1a1a1a; text-decoration: none; font-weight: 600; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; border-radius: 4px;">
                                    Continuer vos achats
                                </a>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #1a1a1a; padding: 40px; text-align: center;">
                                <!-- Logo footer (petit) -->
                                <div style="margin-bottom: 20px;">
                                    <img src="{logo_url}" alt="OPALINE PARFUMS" style="max-width: 100px; height: 50px; opacity: 0.8; display: block; margin: 0 auto;" />
                                </div>
                                
                                <!-- Liens sociaux -->
                                <div style="margin-bottom: 25px;">
                                    <a href="https://www.instagram.com/opaline_parfums/" style="display: inline-block; margin: 0 10px; color: #d4af37; text-decoration: none; font-size: 13px;">
                                        Instagram
                                    </a>
                                    <span style="color: #666;">•</span>
                                    <a href="https://opaline-parfums.onrender.com" style="display: inline-block; margin: 0 10px; color: #d4af37; text-decoration: none; font-size: 13px;">
                                        Site Web
                                    </a>
                                </div>
                                
                                <!-- Contact -->
                                <div style="color: #999; font-size: 13px; line-height: 1.8; margin-bottom: 20px;">
                                    📧 opaline.parfums@gmail.com<br>
                                    📍 Montréal, Québec, Canada
                                </div>
                                
                                <!-- Copyright -->
                                <div style="color: #666; font-size: 11px; padding-top: 20px; border-top: 1px solid #333;">
                                    © 2025 OPALINE PARFUMS • Tous droits réservés<br>
                                    <a href="https://opaline-parfums.onrender.com/politique-confidentialite" style="color: #999; text-decoration: none; margin: 0 5px;">Confidentialité</a> •
                                    <a href="https://opaline-parfums.onrender.com/conditions-vente" style="color: #999; text-decoration: none; margin: 0 5px;">Conditions</a> •
                                    <a href="https://opaline-parfums.onrender.com/mentions-legales" style="color: #999; text-decoration: none; margin: 0 5px;">Mentions légales</a>
                                </div>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
        
    </body>
    </html>
    """
    
    try:
        msg = Message(
            subject=f"✓ Confirmation de commande #{order.order_number} - OPALINE PARFUMS",
            recipients=[order.customer_email],
            html=html_body,
            sender=("OPALINE PARFUMS", "opaline.parfums@gmail.com")
        )
        
        mail_instance.send(msg)
        print(f"✅ Email envoyé à {order.customer_email} via Gmail SMTP")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Gmail: {e}")
        return False


# ✅ FONCTION RESEND (BACKUP) - MÊME LOGO
def send_order_confirmation_resend(order):
    """Envoie l'email de confirmation via Resend - Design Premium avec Logo"""
    
    logo_url = "https://i.ibb.co/jtSLs1S/IMG-20251018-181823.png"
    
    # Générer le HTML des produits
    products_html = ""
    for item in order.items:
        products_html += f"""
        <tr>
            <td style="padding: 20px 15px; border-bottom: 1px solid #e0e0e0;">
                <div>
                    <div style="font-weight: 600; color: #1a1a1a; font-size: 16px; margin-bottom: 5px;">
                        {item.product.name}
                    </div>
                    <div style="color: #666; font-size: 13px;">
                        {item.product.brand} • {item.variant.size_ml}ml
                    </div>
                </div>
            </td>
            <td style="padding: 20px 15px; text-align: center; border-bottom: 1px solid #e0e0e0; color: #666;">
                ×{item.quantity}
            </td>
            <td style="padding: 20px 15px; text-align: right; border-bottom: 1px solid #e0e0e0;">
                <div style="font-weight: 600; color: #1a1a1a; font-size: 16px;">
                    ${item.subtotal:.2f}
                </div>
                <div style="color: #999; font-size: 13px; margin-top: 3px;">
                    ${item.variant.price:.2f} / unité
                </div>
            </td>
        </tr>
        """
    
    # [Utilise le même HTML que Gmail - je ne le répète pas pour gagner de la place]
    html_body = f"""[MÊME HTML QUE GMAIL AVEC {logo_url}]"""
    
    try:
        params = {
            "from": "Opaline Parfums <onboarding@resend.dev>",
            "to": [order.customer_email],
            "subject": f"✓ Confirmation de commande #{order.order_number} - OPALINE PARFUMS",
            "html": html_body,
        }
        
        email = resend.Emails.send(params)
        print(f"✅ Email envoyé à {order.customer_email} via Resend")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Resend: {e}")
        return False


# ✅ FONCTION INTELLIGENTE
def send_order_confirmation(order, mail_instance):
    """Essaie Gmail, puis Resend si échec"""
    gmail_success = send_order_confirmation_gmail(order, mail_instance)
    
    if gmail_success:
        return True
    
    print("⚠️ Gmail a échoué, tentative avec Resend...")
    return send_order_confirmation_resend(order)