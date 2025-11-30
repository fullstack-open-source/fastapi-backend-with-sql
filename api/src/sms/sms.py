import os
import requests
from twilio.rest import Client
from src.logger.logger import logger

# -----------------------
# GLOBAL VARIABLES
# -----------------------
# WhatsApp CONFIG - All values must be set via environment variables
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.environ.get("TWILIO_WHATSAPP_NUMBER")
TWILIO_MESSAGING_SERVICE_ID = os.environ.get("TWILIO_MESSAGING_SERVICE_ID")
TWILIO_CONTENT_ID = os.environ.get("TWILIO_CONTENT_ID")
# SMS CONFIG - All values must be set via environment variables
SMS_API_ENDPOINT = os.environ.get("SMS_API_ENDPOINT")
SMS_SENDER_USERNAME = os.environ.get("SMS_SENDER_USERNAME")
SMS_SENDER_PASSWORD = os.environ.get("SMS_SENDER_PASSWORD")
SMS_SENDER = os.environ.get("SMS_SENDER")
SMS_SENDER_MODE = os.environ.get("SMS_SENDER_MODE", "1")

# -----------------------
# FUNCTIONS
# -----------------------

def send_sms(to_number: str, message: str):
    """Send SMS using KWT SMS API."""
    params = {
        "username": SMS_SENDER_USERNAME,
        "password": SMS_SENDER_PASSWORD,
        "sender": SMS_SENDER,
        "mobile": to_number.replace("+", ""),
        "lang": "1",
        "test": SMS_SENDER_MODE,
        "message": message
    }
    try:
        resp = requests.post(SMS_API_ENDPOINT, data=params)
        if resp.text:
            return {"success": True, "data": resp.text}
        else:
            logger.error("Failed to send SMS: Empty response from SMS API", module="SMS")
            return {"success": False, "message": "Failed to send message"}
    except Exception as e:
        logger.error(f"Error sending SMS to {to_number}: {e}", exc_info=True, module="SMS")
        return {"success": False, "error": str(e)}

def send_whatsapp(to_number: str, otp: str):
    """Send WhatsApp message via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{to_number}",
            body=f"Your OTP is: {otp}"
        )
        return {"success": True, "sid": message.sid}
    except Exception as e:
        logger.error(f"Error sending WhatsApp to {to_number}: {e}", exc_info=True, module="SMS")
        return {"success": False, "error": str(e)}

