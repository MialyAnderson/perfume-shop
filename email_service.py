# email_service.py
import resend
import os
from flask_mail import Mail, Message

# Configuration Resend
resend.api_key = os.environ.get("RESEND_API_KEY", "re_bqZgxv8L_9j1JvSJKzYRUfh3S7zFPMAJv")

# ✅ FONCTION GMAIL (PRIORITAIRE)
def send_order_confirmation_gmail(order, mail_instance):
    """Envoie l'email de confirmation via Gmail SMTP"""
    
    # Générer le HTML des produits
    products_html = ""
    for item in order.items:
        products_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 10px;">
                {item.product.name}<br>
                <small style="color: #666;">({item.variant.size_ml}ml)</small>
            </td>
            <td style="padding: 10px; text-align: center;">{item.quantity}</td>
            <td style="padding: 10px; text-align: right;">${item.variant.price:.2f}</td>
            <td style="padding: 10px; text-align: right;"><strong>${item.subtotal:.2f}</strong></td>
        </tr>
        """
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <div style="background-color: #000000; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0;">OPALINE PARFUMS</h1>
            </div>
            
            <div style="padding: 40px 30px; background-color: #f9f9f9;">
                <h2 style="color: #333;">Merci pour votre commande !</h2>
                <p>Bonjour {order.customer_first_name} {order.customer_last_name},</p>
                <p>Votre commande a été confirmée avec succès.</p>
                
                <div style="background-color: #fff; padding: 25px; border-radius: 8px; margin: 25px 0;">
                    <h3>Commande #{order.order_number}</h3>
                    <p><strong>Date :</strong> {order.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                        <thead>
                            <tr style="background-color: #f0f0f0;">
                                <th style="padding: 12px; text-align: left;">Produit</th>
                                <th style="padding: 12px; text-align: center;">Qté</th>
                                <th style="padding: 12px; text-align: right;">Prix unit.</th>
                                <th style="padding: 12px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products_html}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" style="padding: 15px 10px; text-align: right; border-top: 2px solid #333;"><strong>TOTAL :</strong></td>
                                <td style="padding: 15px 10px; text-align: right; border-top: 2px solid #333; font-size: 18px;"><strong>${order.total_amount:.2f} CAD</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <div style="margin-top: 25px; padding: 15px; background-color: #f9f9f9;">
                        <h4>Adresse de livraison :</h4>
                        <p>{order.shipping_address}</p>
                        <p>{order.shipping_city}, {order.shipping_postal_code}</p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <p><strong>Email :</strong> {order.customer_email}</p>
                        <p><strong>Téléphone :</strong> {order.customer_phone}</p>
                    </div>
                </div>
                
                <p>Votre commande sera traitée dans les plus brefs délais.</p>
                <p>Merci de votre confiance !</p>
                <p><strong>L'équipe OPALINE PARFUMS</strong></p>
            </div>
            
            <div style="background-color: #333; padding: 25px; text-align: center; color: #fff;">
                <p style="margin: 0;">© 2025 OPALINE PARFUMS - Tous droits réservés</p>
                <p style="margin: 5px 0 0 0;">Contact : opaline.parfums@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        msg = Message(
            subject=f"Confirmation de commande #{order.order_number} - OPALINE PARFUMS",
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


# ✅ FONCTION RESEND (BACKUP)
def send_order_confirmation_resend(order):
    """Envoie l'email de confirmation via Resend (BACKUP)"""
    
    # Générer le HTML des produits
    products_html = ""
    for item in order.items:
        products_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
            <td style="padding: 10px;">
                {item.product.name}<br>
                <small style="color: #666;">({item.variant.size_ml}ml)</small>
            </td>
            <td style="padding: 10px; text-align: center;">{item.quantity}</td>
            <td style="padding: 10px; text-align: right;">${item.variant.price:.2f}</td>
            <td style="padding: 10px; text-align: right;"><strong>${item.subtotal:.2f}</strong></td>
        </tr>
        """
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <div style="background-color: #000000; padding: 30px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0;">OPALINE PARFUMS</h1>
            </div>
            
            <div style="padding: 40px 30px; background-color: #f9f9f9;">
                <h2 style="color: #333;">Merci pour votre commande !</h2>
                <p>Bonjour {order.customer_first_name} {order.customer_last_name},</p>
                <p>Votre commande a été confirmée avec succès.</p>
                
                <div style="background-color: #fff; padding: 25px; border-radius: 8px; margin: 25px 0;">
                    <h3>Commande #{order.order_number}</h3>
                    <p><strong>Date :</strong> {order.created_at.strftime('%d/%m/%Y à %H:%M')}</p>
                    
                    <table style="width: 100%; border-collapse: collapse; margin: 25px 0;">
                        <thead>
                            <tr style="background-color: #f0f0f0;">
                                <th style="padding: 12px; text-align: left;">Produit</th>
                                <th style="padding: 12px; text-align: center;">Qté</th>
                                <th style="padding: 12px; text-align: right;">Prix unit.</th>
                                <th style="padding: 12px; text-align: right;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products_html}
                        </tbody>
                        <tfoot>
                            <tr>
                                <td colspan="3" style="padding: 15px 10px; text-align: right; border-top: 2px solid #333;"><strong>TOTAL :</strong></td>
                                <td style="padding: 15px 10px; text-align: right; border-top: 2px solid #333; font-size: 18px;"><strong>${order.total_amount:.2f} CAD</strong></td>
                            </tr>
                        </tfoot>
                    </table>
                    
                    <div style="margin-top: 25px; padding: 15px; background-color: #f9f9f9;">
                        <h4>Adresse de livraison :</h4>
                        <p>{order.shipping_address}</p>
                        <p>{order.shipping_city}, {order.shipping_postal_code}</p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <p><strong>Email :</strong> {order.customer_email}</p>
                        <p><strong>Téléphone :</strong> {order.customer_phone}</p>
                    </div>
                </div>
                
                <p>Votre commande sera traitée dans les plus brefs délais.</p>
                <p>Merci de votre confiance !</p>
                <p><strong>L'équipe OPALINE PARFUMS</strong></p>
            </div>
            
            <div style="background-color: #333; padding: 25px; text-align: center; color: #fff;">
                <p style="margin: 0;">© 2025 OPALINE PARFUMS - Tous droits réservés</p>
                <p style="margin: 5px 0 0 0;">Contact : opaline.parfums@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        params = {
            "from": "Opaline Parfums <onboarding@resend.dev>",
            "to": [order.customer_email],
            "subject": f"Confirmation de commande #{order.order_number} - OPALINE PARFUMS",
            "html": html_body,
        }
        
        email = resend.Emails.send(params)
        print(f"✅ Email envoyé à {order.customer_email} via Resend (ID: {email['id']})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Resend: {e}")
        return False


# ✅ FONCTION INTELLIGENTE (essaie Gmail, puis Resend si échec)
def send_order_confirmation(order, mail_instance):
    """
    Essaie d'envoyer via Gmail d'abord.
    Si échec, utilise Resend comme backup.
    """
    # Essayer Gmail d'abord
    gmail_success = send_order_confirmation_gmail(order, mail_instance)
    
    if gmail_success:
        return True
    
    # Si Gmail échoue, essayer Resend
    print("⚠️ Gmail a échoué, tentative avec Resend...")
    return send_order_confirmation_resend(order)