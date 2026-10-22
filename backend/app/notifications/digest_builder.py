"""Digest Builder — renders the Jinja2 email templates for each notification type."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

TEMPLATES_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_digest(farmer_name: str, schemes: list[dict]) -> tuple[str, str]:
    subject = f"Your weekly scheme matches ({len(schemes)})"
    body = _env.get_template("digest.html").render(
        farmer_name=farmer_name, schemes=schemes, app_base_url=settings.APP_BASE_URL
    )
    return subject, body


def render_alert(
    farmer_name: str, scheme_name: str, scheme_code: str
) -> tuple[str, str]:
    subject = f"New scheme published: {scheme_name}"
    body = _env.get_template("alert.html").render(
        farmer_name=farmer_name,
        scheme_name=scheme_name,
        scheme_code=scheme_code,
        app_base_url=settings.APP_BASE_URL,
    )
    return subject, body


def render_status(
    farmer_name: str, scheme_name: str, status: str, note: str | None
) -> tuple[str, str]:
    subject = f"Your {scheme_name} application was {status}"
    body = _env.get_template("status.html").render(
        farmer_name=farmer_name,
        scheme_name=scheme_name,
        status=status,
        note=note,
        app_base_url=settings.APP_BASE_URL,
    )
    return subject, body
