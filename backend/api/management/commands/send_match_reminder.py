from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event, MatchSubmission, Registration
from api.services.emails import send_match_form_reminder


class Command(BaseCommand):
    help = "Send match form reminder emails to confirmed registrations that have not submitted."

    def handle(self, *args, **options):
        yesterday = (timezone.now() - timedelta(days=1)).date()
        events = Event.objects.filter(event_date__date=yesterday)
        self.stdout.write(f"Found {events.count()} event(s) from yesterday.")
        count = 0
        for event in events:
            registrations = Registration.objects.filter(
                event=event, status="confirmed"
            ).select_related("attendee", "event")
            for reg in registrations:
                has_submitted = MatchSubmission.objects.filter(
                    event=event, submitted_by=reg
                ).exists()
                if not has_submitted:
                    send_match_form_reminder(reg)
                    count += 1
                    self.stdout.write(f"  Sent match form reminder to {reg.attendee.email}")
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} registration(s)."))
