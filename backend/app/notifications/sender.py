"""
Email Sender — Spec Section 16, notifications.

EmailSender ABC: send(to, subject, html_body) -> None.
  ConsoleEmailSender prints to stdout (used in dev / EMAIL_BACKEND=console).
  SmtpEmailSender sends via smtplib (used in prod / EMAIL_BACKEND=smtp,
  points at MailHog in dev-with-smtp mode).
"""

from __future__ import annotations

import smtplib
from abc import ABC, abstractmethod
from email.mime.text import MIMEText

from app.core.config import settings


class EmailSender(ABC):
    @abstractmethod
    def send(self, to: str, subject: str, html_body: str) -> None: ...


class ConsoleEmailSender(EmailSender):
    """Prints the email to stdout instead of sending it — used in dev/tests."""

    def send(self, to: str, subject: str, html_body: str) -> None:
        print(
            f"--- EMAIL to={to} subject={subject!r} ---\n{html_body}\n--- END EMAIL ---"
        )


class SmtpEmailSender(EmailSender):
    def send(self, to: str, subject: str, html_body: str) -> None:
        message = MIMEText(html_body, "html")
        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = to

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
            if settings.SMTP_USER:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.sendmail(settings.EMAIL_FROM, [to], message.as_string())


def get_email_sender() -> EmailSender:
    if settings.EMAIL_BACKEND == "smtp":
        return SmtpEmailSender()
    return ConsoleEmailSender()
