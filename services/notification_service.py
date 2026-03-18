import os
import requests
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_telegram_alert(title: str, current_price: float, target_price: float, url: str) -> bool:
    """
    Sends a price drop alert message via Telegram Bot.
    """
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logger.warning("Telegram credentials missing in .env")
        return False
        
    message = (
        f"🚨 *Price Drop Alert!*\n\n"
        f"📦 *Product:* {title}\n"
        f"💰 *Current Price:* ₹{current_price:,.2f}\n"
        f"🎯 *Target Price:* ₹{target_price:,.2f}\n\n"
        f"🔗 [Buy Now]({url})"
    )
    
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False

def send_email_alert(title: str, current_price: float, target_price: float, url: str) -> bool:
    """
    Sends a price drop alert via Email (as an alternative fallback).
    """
    email_user: str | None = os.environ.get("EMAIL_USER")
    email_pass: str | None = os.environ.get("EMAIL_PASS")
    
    if not email_user or not email_pass:
        return False
        
    msg = EmailMessage()
    msg['Subject'] = f"Price Drop Alert: {title[0:30]}..."
    msg['From'] = email_user
    msg['To'] = email_user
    
    content = (
        f"Price Drop Alert!\n\n"
        f"Product: {title}\n"
        f"Current Price: ₹{current_price:,.2f}\n"
        f"Target Price: ₹{target_price:,.2f}\n\n"
        f"Link: {url}"
    )
    msg.set_content(content)
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(str(email_user), str(email_pass))
            smtp.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send Email alert: {e}")
        return False

def trigger_alert(title: str, current_price: float, target_price: float, url: str) -> bool:
    """
    Primary alert function that tries Telegram first, then falls back to email.
    """
    if send_telegram_alert(title, current_price, target_price, url):
        return True
    return send_email_alert(title, current_price, target_price, url)
