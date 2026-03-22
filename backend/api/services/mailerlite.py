import httpx
from django.conf import settings

MAILERLITE_API_URL = "https://connect.mailerlite.com/api"


def _get_headers():
    return {
        "Authorization": f"Bearer {settings.MAILERLITE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def send_email(to_email, subject, html_content):
    """Send a transactional email via MailerLite."""
    if not settings.MAILERLITE_API_KEY:
        print(f"[MailerLite] Skipping email to {to_email} (no API key configured)")
        return None
    response = httpx.post(
        f"{MAILERLITE_API_URL}/campaigns",
        headers=_get_headers(),
        json={
            "to": [{"email": to_email}],
            "subject": subject,
            "html": html_content,
        },
        timeout=30,
    )
    return response


def add_subscriber(email, first_name, last_name, fields=None):
    """Add or update a subscriber in MailerLite."""
    if not settings.MAILERLITE_API_KEY:
        print(f"[MailerLite] Skipping subscriber add for {email} (no API key configured)")
        return None
    data = {
        "email": email,
        "fields": {
            "name": first_name,
            "last_name": last_name,
            **(fields or {}),
        },
    }
    response = httpx.post(
        f"{MAILERLITE_API_URL}/subscribers",
        headers=_get_headers(),
        json=data,
        timeout=30,
    )
    return response
