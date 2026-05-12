import os
import random
import smtplib
from email.message import EmailMessage


def generate_verification_code():
    return str(random.randint(100000, 999999))


def get_secret(name, default=None):
    try:
        import streamlit as st

        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)


def send_verification_email(to_email, code):
    smtp_host = get_secret("SMTP_HOST")
    smtp_port = int(get_secret("SMTP_PORT", "587"))
    smtp_user = get_secret("SMTP_USER")
    smtp_password = get_secret("SMTP_PASSWORD")
    smtp_from = get_secret("SMTP_FROM", smtp_user)

    if not smtp_host or not smtp_user or not smtp_password or not smtp_from:
        return False, "Email verification is not configured."

    message = EmailMessage()
    message["Subject"] = "Your AI CV Analyzer verification code"
    message["From"] = smtp_from
    message["To"] = to_email
    message.set_content(
        "Hello,\n\n"
        "Thank you for choosing AI CV Analyzer and for trusting us with your career journey.\n"
        "We are happy to help you analyze your CV, discover relevant opportunities, "
        "and improve your professional profile.\n\n"
        f"Your email verification code is: {code}\n\n"
        "Please enter this code in the app to complete your account creation.\n\n"
        "If you did not request this code, you can safely ignore this email.\n\n"
        "Best regards,\n"
        "Ayoub Leader of AI CV Analyzer Team"
    )

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(message)

        return True, "Verification code sent. Please check your email."

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check your Gmail App Password."
    except smtplib.SMTPConnectError:
        return False, "Could not connect to the SMTP server. Check SMTP_HOST and SMTP_PORT."
    except smtplib.SMTPException as error:
        return False, f"SMTP error: {error}"
    except Exception as error:
        return False, f"Email sending error: {error}"
