import smtplib
import json
import urllib.request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database.connection import settings


def send_verification_email(email: str, token: str):
    """
    Sends email verification via Brevo (formerly Sendinblue).
    Supports both Brevo HTTPS Transactional API (recommended on cloud like Render)
    and Brevo SMTP relay (port 587).
    """
    verification_link = (
        f"{settings.BACKEND_BASE_URL}/auth/verify-email?token={token}"
    )

    email_body = f"""
    <!DOCTYPE html>
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #2563eb; padding: 20px; text-align: center; border-radius: 12px 12px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 24px;">Reading Nova</h1>
                <p style="color: #dbeafe; margin: 5px 0 0 0; font-size: 14px;">A perfect place for readers and writers</p>
            </div>
            
            <div style="border: 1px solid #e2e8f0; border-top: none; padding: 30px; border-radius: 0 0 12px 12px; background: #ffffff;">
                <h2 style="color: #1e293b; margin-top: 0;">Verify Your Email Address</h2>
                <p>Thank you for registering at Reading Nova! Please verify your email address to activate your account and start ordering.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_link}" style="background-color: #2563eb; color: white; padding: 12px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 15px; display: inline-block;">
                        Verify My Email
                    </a>
                </div>
                
                <p style="font-size: 12px; color: #64748b; margin-top: 25px;">
                    This link will expire in 24 hours. If you did not create this account, please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """

    # Strategy 1: Brevo HTTP REST API (Best for Render/Vercel cloud where SMTP ports can be throttled)
    if settings.BREVO_API_KEY:
        try:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json"
            }
            data = {
                "sender": {
                    "name": "Reading Nova",
                    "email": settings.MAIL_FROM or "no-reply@readingnova.com"
                },
                "to": [{"email": email}],
                "subject": "Verify Your Email Address - Reading Nova",
                "htmlContent": email_body
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (200, 201):
                    return True
        except Exception as e:
            print(f"Brevo API error: {e}, attempting SMTP fallback...")

    # Strategy 2: Brevo SMTP Relay (smtp-relay.brevo.com:587)
    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify Your Email Address - Reading Nova"
    message["From"] = settings.MAIL_FROM or "Reading Nova <no-reply@readingnova.com>"
    message["To"] = email

    html_part = MIMEText(email_body, "html")
    message.attach(html_part)

    with smtplib.SMTP(
        settings.MAIL_SERVER or "smtp-relay.brevo.com",
        settings.MAIL_PORT or 587
    ) as server:
        server.starttls()
        server.login(
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD
        )
        server.sendmail(
            settings.MAIL_FROM or settings.MAIL_USERNAME,
            email,
            message.as_string()
        )
    return True