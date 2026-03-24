import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event, MarketingEmailLog, Registration
from api.services.emails import MARKETING_SCHEDULE, render_marketing_email
from api.services.mailerlite import create_campaign, get_total_subscriber_count

logger = logging.getLogger("api.commands.send_marketing_emails")


def _is_event_full(event):
    """Check if an event has reached capacity (confirmed + pending)."""
    reserved = Registration.objects.filter(event=event, status__in=("confirmed", "pending")).count()
    return reserved >= event.capacity


class Command(BaseCommand):
    help = "Send scheduled marketing emails for the next upcoming open event."

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()

        event = Event.objects.filter(status="open", event_date__gt=now).order_by("event_date").first()
        if not event:
            if options["verbosity"] >= 2:
                self.stdout.write("No upcoming open events found.")
            return

        days_until = (event.event_date.date() - today).days
        full = _is_event_full(event)

        for email_key, days_before in MARKETING_SCHEDULE:
            if days_until > days_before:
                continue

            # Skip if too late (more than 3 days past the intended send date)
            if days_before - days_until > 3:
                if options["verbosity"] >= 2:
                    self.stdout.write(
                        f"  Skipping {email_key}: too late (intended {days_before}d before, now {days_until}d before)"
                    )
                continue

            # Skip if already sent
            if MarketingEmailLog.objects.filter(event=event, email_key=email_key).exists():
                if options["verbosity"] >= 2:
                    self.stdout.write(f"  Skipping {email_key}: already sent")
                continue

            subject, html = render_marketing_email(email_key, event, full=full)
            campaign_name = f"{email_key}_{event.id}"

            try:
                subscriber_count = get_total_subscriber_count()
                result = create_campaign(campaign_name, subject, html)
                if result is None:
                    if options["verbosity"] >= 1:
                        self.stdout.write(f"  Skipping {email_key}: no MailerLite API key configured")
                    continue
                MarketingEmailLog.objects.create(
                    event=event,
                    email_key=email_key,
                    subscriber_count=subscriber_count,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"  Sent {email_key} for event {event} to {subscriber_count} subscribers")
                )
            except Exception:
                logger.exception("Failed to send marketing email %s for event %s", email_key, event)
                self.stderr.write(f"  Failed to send {email_key} for event {event}")
