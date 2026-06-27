# =============================================
# ECOMMERCE PREDICTIVE PRICE TRACKING SYSTEM
# Email Alerts File
# =============================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SENDER_EMAIL, SENDER_APP_PASSWORD, PRICE_DROP_ALERT_PERCENTAGE

# --- Send Email ---
def send_email(receiver_email, subject, body):
    try:
        # Setup email
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        # Connect to Gmail
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        print(f"Email sent to {receiver_email}")
        return True

    except Exception as e:
        print(f"Email error: {e}")
        return False

# --- Check Target Price Alert ---
def check_target_price_alert(product_name, current_price, target_price, site, url, receiver_email):
    try:
        if current_price <= target_price:
            subject = f"🎯 Target Price Reached! {product_name}"
            body = f"""
            <html>
            <body>
            <h2 style="color: green;">🎯 Target Price Reached!</h2>
            <p>Great news! <b>{product_name}</b> has reached your target price!</p>
            <table border="1" cellpadding="10">
                <tr><td><b>Product</b></td><td>{product_name}</td></tr>
                <tr><td><b>Your Target Price</b></td><td>₹{target_price}</td></tr>
                <tr><td><b>Current Price</b></td><td style="color:green;">₹{current_price}</td></tr>
                <tr><td><b>Best Site</b></td><td>{site}</td></tr>
            </table>
            <br>
            <a href="{url}" style="background-color: green; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Buy Now</a>
            <br><br>
            <p>— Ecommerce Predictive Price Tracking System</p>
            </body>
            </html>
            """
            send_email(receiver_email, subject, body)
            return True
        return False

    except Exception as e:
        print(f"Target price alert error: {e}")
        return False

# --- Check Sudden Price Drop Alert ---
def check_price_drop_alert(product_name, old_price, current_price, site, url, receiver_email):
    try:
        if old_price and old_price > 0:
            drop_percentage = ((old_price - current_price) / old_price) * 100

            if drop_percentage >= PRICE_DROP_ALERT_PERCENTAGE:
                subject = f"📉 Price Drop Alert! {product_name}"
                body = f"""
                <html>
                <body>
                <h2 style="color: orange;">📉 Sudden Price Drop!</h2>
                <p><b>{product_name}</b> price has dropped by <b style="color:red;">{round(drop_percentage, 2)}%!</b></p>
                <table border="1" cellpadding="10">
                    <tr><td><b>Product</b></td><td>{product_name}</td></tr>
                    <tr><td><b>Yesterday Price</b></td><td>₹{old_price}</td></tr>
                    <tr><td><b>Current Price</b></td><td style="color:green;">₹{current_price}</td></tr>
                    <tr><td><b>Drop</b></td><td style="color:red;">{round(drop_percentage, 2)}%</td></tr>
                    <tr><td><b>Best Site</b></td><td>{site}</td></tr>
                </table>
                <br>
                <a href="{url}" style="background-color: orange; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Buy Now</a>
                <br><br>
                <p>— Ecommerce Predictive Price Tracking System</p>
                </body>
                </html>
                """
                send_email(receiver_email, subject, body)
                return True
        return False

    except Exception as e:
        print(f"Price drop alert error: {e}")
        return False