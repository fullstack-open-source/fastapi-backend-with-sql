from src.email.templete import ONETIME_VERIFICATION_TEMPLATE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import smtplib
import os

# ==============================
# Email Configuration (Env Vars)
# ==============================
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = True

# ==============================
# Email Sending Function
# ==============================
def send_otp_email(to_email: str, otp: str) -> bool:
    try:
        subject = "One-Time Verification Code"

        # Format HTML with OTP
        html_body = ONETIME_VERIFICATION_TEMPLATE.format(code=otp)

        # Build email
        message = MIMEMultipart("alternative")
        message["From"] = EMAIL_HOST_USER
        message["To"] = to_email
        message["Subject"] = subject

        # Attach both plain text and HTML
        plain_text = f"Your one-time password (OTP) is: {otp}\n\nIt will expire in 10 minutes."
        message.attach(MIMEText(plain_text, "plain"))
        message.attach(MIMEText(html_body, "html"))

        # Send mail
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            if EMAIL_USE_TLS:
                server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, to_email, message.as_string())

        print(f"✅ OTP sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending OTP: {e}")
        return False

# ==============================
# Send in Background Thread
# ==============================
def send_otp_async(to_email: str, otp: str):
    thread = threading.Thread(target=send_otp_email, args=(to_email, otp))
    thread.daemon = True  # ensures thread won't block program exit
    thread.start()
