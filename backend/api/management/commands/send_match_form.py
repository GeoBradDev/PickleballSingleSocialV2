from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event, Registration
from api.services.emails import send_match_form_link


class Command(BaseCommand):
    help = "Send match form link emails to confirmed registrations for events that happened today."

    def handle(self, *args, **options):
        today = timezone.now().date()
        events = Event.objects.filter(event_date__date=today, status="closed")
        self.stdout.write(f"Found {events.count()} closed event(s) that happened today.")
        count = 0
        for event in events:
            registrations = Registration.objects.filter(event=event, status="confirmed").select_related(
                "attendee", "event"
            )
            if not registrations.exists():
                self.stdout.write(f"  No confirmed registrations for {event.title}, skipping.")
                continue
            for reg in registrations:
                send_match_form_link(reg)
                count += 1
                self.stdout.write(f"  Sent match form link to {reg.attendee.email}")
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} registration(s)."))
