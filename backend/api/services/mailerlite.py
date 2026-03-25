import logging

import httpx
from django.conf import settings

logger = logging.getLogger("api.services.mailerlite")

MAILERLITE_API_URL = "https://connect.mailerlite.com/api"


def _get_headers():
    return {
        "Authorization": f"Bearer {settings.MAILERLITE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def send_email(to_email, subject, html_content):
    """Send a transactional email via MailerSend."""
    if not settings.MAILERSEND_API_KEY:
        logger.info("Skipping email to %s (no MailerSend API key configured)", to_email)
        return None
    try:
        response = httpx.post(
            "https://api.mailersend.com/v1/email",
            headers={
                "Authorization": f"Bearer {settings.MAILERSEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": {
                    "email": settings.MAILERLITE_FROM_EMAIL,
                    "name": settings.MAILERLITE_FROM_NAME,
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "html": html_content,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Failed to send email to %s: %s | Status: %d | Response: %s",
            to_email,
            subject,
            exc.response.status_code,
            exc.response.text,
        )
        return None
    except httpx.HTTPError:
        logger.exception("Failed to send email to %s: %s", to_email, subject)
        return None


def add_subscriber(email, first_name, last_name, fields=None, group_ids=None):
    """Add or update a subscriber in MailerLite, optionally assigning to groups."""
    if not settings.MAILERLITE_API_KEY:
        logger.info("Skipping subscriber add for %s (no API key configured)", email)
        return None
    data = {
        "email": email,
        "fields": {
            "name": first_name,
            "last_name": last_name,
            **(fields or {}),
        },
    }
    if group_ids:
        data["groups"] = group_ids
    try:
        response = httpx.post(
            f"{MAILERLITE_API_URL}/subscribers",
            headers=_get_headers(),
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        return response
    except httpx.HTTPError:
        logger.exception("Failed to add subscriber %s", email)
        return None


def create_campaign(name, subject, html_content):
    """Create and immediately send a campaign to all subscribers."""
    if not settings.MAILERLITE_API_KEY:
        logger.info("Skipping campaign '%s' (no API key configured)", name)
        return None

    # Create the campaign (no groups = all active subscribers)
    campaign_data = {
        "name": name,
        "type": "regular",
        "emails": [
            {
                "subject": subject,
                "from": settings.MAILERLITE_FROM_EMAIL,
                "from_name": settings.MAILERLITE_FROM_NAME,
                "content": html_content,
            }
        ],
    }
    create_response = httpx.post(
        f"{MAILERLITE_API_URL}/campaigns",
        headers=_get_headers(),
        json=campaign_data,
        timeout=30,
    )
    create_response.raise_for_status()
    campaign_id = create_response.json()["data"]["id"]

    # Schedule for immediate delivery
    schedule_response = httpx.post(
        f"{MAILERLITE_API_URL}/campaigns/{campaign_id}/schedule",
        headers=_get_headers(),
        json={"delivery": "instant"},
        timeout=30,
    )
    schedule_response.raise_for_status()
    return schedule_response


def get_total_subscriber_count():
    """Return the total active subscriber count."""
    if not settings.MAILERLITE_API_KEY:
        return 0
    response = httpx.get(
        f"{MAILERLITE_API_URL}/subscribers",
        headers=_get_headers(),
        params={"filter[status]": "active", "limit": 1},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["total"]
