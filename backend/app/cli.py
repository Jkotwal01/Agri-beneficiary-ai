"""
CLI entrypoint — `python -m app.cli send_digest`.

Triggers NotificationService.send_weekly_digest() against a real DB session,
printing emails to the console (or sending via SMTP if EMAIL_BACKEND=smtp).
"""

from __future__ import annotations

import sys

from app.core.db import SessionLocal
from app.notifications.sender import get_email_sender
from app.services.notification_service import NotificationService

COMMANDS = ("send_digest",)


def send_digest() -> None:
    db = SessionLocal()
    try:
        sent = NotificationService(db, get_email_sender()).send_weekly_digest()
        print(f"Weekly digest sent to {sent} farmer(s).")
    finally:
        db.close()


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] not in COMMANDS:
        print(f"Usage: python -m app.cli <{'|'.join(COMMANDS)}>")
        return 1

    if argv[1] == "send_digest":
        send_digest()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
