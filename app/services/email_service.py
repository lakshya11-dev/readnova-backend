import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.database.connection import settings


def send_verification_email(email: str, token: str):

    verification_link = (
        f"{settings.BACKEND_BASE_URL}/auth/verify-email?token={token}"
    )

    message = MIMEMultipart("alternative")

    message["Subject"] = "Verify Your Email Address"
    message["From"] = settings.MAIL_FROM
    message["To"] = email

    email_body = f"""
    <html>
        <body>
            <h2>Welcome!</h2>

            <p>Thank you for registering.</p>

            <p>Please verify your email by clicking below:</p>

            <a href="{verification_link}">
                Verify My Email
            </a>

            <p>This link will expire in 24 hours.</p>
        </body>
    </html>
    """

    html_part = MIMEText(email_body, "html")

    message.attach(html_part)

    with smtplib.SMTP(
        settings.MAIL_SERVER,
        settings.MAIL_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.MAIL_USERNAME,
            settings.MAIL_PASSWORD
        )

        server.sendmail(
            settings.MAIL_FROM,
            email,
            message.as_string()
        )