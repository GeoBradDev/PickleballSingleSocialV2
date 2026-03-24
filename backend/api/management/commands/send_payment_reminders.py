from django.core.management.base import BaseCommand

from api.models import Event, Registration
from api.services.emails import send_payment_reminder


class Command(BaseCommand):
    help = "Send payment reminder emails to pending registrations for open events."

    def handle(self, *args, **options):
        events = Event.objects.filter(status="open")
        self.stdout.write(f"Found {events.count()} open event(s).")
        count = 0
        for event in events:
            registrations = Registration.objects.filter(event=event, status="pending").select_related(
                "attendee", "event"
            )
            for reg in registrations:
                send_payment_reminder(reg)
                count += 1
                self.stdout.write(f"  Sent payment reminder to {reg.attendee.email}")
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} registration(s)."))
