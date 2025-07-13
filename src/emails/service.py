from email.message import EmailMessage
from pathlib import Path

import aiosmtplib
import logfire
from fastapi import HTTPException, status
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession

from src.emails.dao import EmailDAO
from src.settings.config import settings

# Path: src/emails/service/templates/verification_email.html
TEMPLATE_DIR = Path(__file__).parent / "templates"
ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


async def send_email(recipient: str, subject: str, body: str) -> None:
    """Send an email asynchronously using aiosmtplib."""
    message = EmailMessage()
    message["From"] = settings.email_service.EMAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body, subtype="html")

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.email_service.SMTP_HOST,
            port=settings.email_service.SMTP_PORT,
            username=settings.email_service.SMTP_USERNAME,
            password=settings.email_service.SMTP_PASSWORD,
            start_tls=settings.email_service.SMTP_STARTTLS,
        )
    except Exception as e:
        logfire.error(f"Failed to send email to {recipient}", error=e)


def render_verification_email(user_email: str, verification_link: str) -> str:
    """Render template with jinja2 tool, html templates are located in /templates dir."""
    template = ENV.get_template("verification_template.html")
    return template.render(user_email=user_email, verification_link=verification_link)


def render_password_recovery_email(user_email: str, recovery_link: str) -> str:
    """Render template with jinja2 tool, html templates are located in /templates dir."""
    template = ENV.get_template("password_recovery_template.html")
    return template.render(user_email=user_email, recovery_link=recovery_link)


async def emails_limit_handler(db: AsyncSession, user_id: int):
    """
    Exceptions handler for emails limit.

    1. Get user and global daily email record.
    2. Raise an exception if user or global daily emails limit is reached.
    3. If all good -> increment user daily email record.
    """
    user_daily_record = await EmailDAO.get_user_daily_email_record(db, user_id)
    global_daily_record = await EmailDAO.get_global_daily_email_record(db)
    if (
        user_daily_record
        and user_daily_record.emails_counter >= settings.USER_DAILY_LIMIT
        or global_daily_record >= settings.GLOBAL_DAILY_LIMIT
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Your daily emails limit has been reached",
        )
    await EmailDAO.increment_emails_count(db, user_id)
