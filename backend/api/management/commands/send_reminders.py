from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event, Registration
from api.services.emails import send_reminder


class Command(BaseCommand):
    help = "Send 3-day-before reminder emails to confirmed registrations."

    def handle(self, *args, **options):
        now = timezone.now()
        cutoff = now + timedelta(days=3)
        events = Event.objects.filter(
            event_date__gte=now,
            event_date__lte=cutoff,
            status__in=["open", "closed"],
        )
        self.stdout.write(f"Found {events.count()} event(s) within 3 days.")
        count = 0
        for event in events:
            registrations = Registration.objects.filter(
                event=event, status="confirmed"
            ).select_related("attendee", "event")
            for reg in registrations:
                send_reminder(reg)
                count += 1
                self.stdout.write(f"  Sent reminder to {reg.attendee.email}")
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} registration(s)."))
