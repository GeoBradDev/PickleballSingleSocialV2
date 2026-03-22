from django.core.management.base import BaseCommand

from api.models import Match
from api.services.emails import send_match_notification


class Command(BaseCommand):
    help = "Send match notification emails for unnotified matches."

    def handle(self, *args, **options):
        matches = Match.objects.filter(notified=False).select_related(
            "event",
            "attendee_a",
            "attendee_a__attendee",
            "attendee_b",
            "attendee_b__attendee",
        )
        self.stdout.write(f"Found {matches.count()} unnotified match(es).")
        for match in matches:
            send_match_notification(match)
            match.notified = True
            match.save()
            self.stdout.write(
                f"  Notified match: {match.attendee_a.attendee.email} <-> {match.attendee_b.attendee.email}"
            )
        self.stdout.write(self.style.SUCCESS("Done."))
