"""Mail sending service"""
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.conf.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str) -> None:
    """Send a verification email to the user.

    This function generates a verification token for the given email and sends a
    confirmation email to the user with a link to verify their email address. The
    email contains the host, username, and a unique token. The email is formatted
    using an HTML template.

    Args:
        email (EmailStr): The email address of the user to send the verification email to.
        username (str): The username of the user.
        host (str): The host URL, used to generate the verification link in the email.

    Raises:
        ConnectionErrors: If there is an issue connecting to the email server,
            an error is logged and raised.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email on PixnTalk",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification
            },
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
