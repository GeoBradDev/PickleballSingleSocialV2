from collections import defaultdict

from django.core.management.base import BaseCommand

from api.models import Match
from api.services.emails import send_combined_match_notification


class Command(BaseCommand):
    help = "Send match notification emails for unnotified matches."

    def handle(self, *args, **options):
        matches = list(
            Match.objects.filter(notified=False).select_related(
                "event",
                "attendee_a",
                "attendee_a__attendee",
                "attendee_b",
                "attendee_b__attendee",
            )
        )
        self.stdout.write(f"Found {len(matches)} unnotified match(es).")

        # Group matches by (event, registration) so each person gets one email
        grouped = defaultdict(list)
        for match in matches:
            grouped[(match.event, match.attendee_a)].append(match.attendee_b)
            grouped[(match.event, match.attendee_b)].append(match.attendee_a)

        for (event, registration), matched_registrations in grouped.items():
            send_combined_match_notification(event, registration, matched_registrations)
            self.stdout.write(
                f"  Notified {registration.attendee.email} with {len(matched_registrations)} match(es)"
            )

        for match in matches:
            match.notified = True
            match.save()

        self.stdout.write(self.style.SUCCESS("Done."))
