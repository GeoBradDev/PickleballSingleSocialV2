import logging
from itertools import combinations

from django.core.management.base import BaseCommand

from api.models import Event, Match, MatchSubmission, Registration

logger = logging.getLogger("api.commands.process_matches")


class Command(BaseCommand):
    help = "Process match submissions and create Match records for mutual selections."

    def handle(self, *args, **options):
        # Find completed events that have no Match records yet
        events = Event.objects.filter(status="completed").exclude(matches__isnull=False)
        self.stdout.write(f"Found {events.count()} completed event(s) to process.")
        total_matches = 0
        for event in events:
            submissions = MatchSubmission.objects.filter(event=event).prefetch_related("selected_attendees")
            if not submissions.exists():
                self.stdout.write(f"  No submissions for {event.title}, skipping.")
                continue

            # Only consider submissions from confirmed registrations
            confirmed_ids = set(
                Registration.objects.filter(event=event, status="confirmed").values_list("id", flat=True)
            )

            # Build a dict: registration_id -> set of selected registration_ids
            selections = {}
            for sub in submissions:
                if sub.submitted_by_id not in confirmed_ids:
                    continue
                selected_ids = set(sub.selected_attendees.values_list("id", flat=True)) & confirmed_ids
                selections[sub.submitted_by_id] = selected_ids

            # Find mutual matches among all pairs of submitters
            submitter_ids = list(selections.keys())
            for reg_a_id, reg_b_id in combinations(submitter_ids, 2):
                if reg_b_id in selections.get(reg_a_id, set()) and reg_a_id in selections.get(reg_b_id, set()):
                    Match.objects.create(
                        event=event,
                        attendee_a_id=reg_a_id,
                        attendee_b_id=reg_b_id,
                    )
                    total_matches += 1
                    self.stdout.write(f"  Created match: Registration {reg_a_id} <-> Registration {reg_b_id}")

            if not total_matches:
                logger.info("No mutual matches found for event %d: %s", event.id, event.title)

        self.stdout.write(self.style.SUCCESS(f"Done. Created {total_matches} match(es)."))
