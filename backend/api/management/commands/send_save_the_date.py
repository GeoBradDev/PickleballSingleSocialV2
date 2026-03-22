from django.core.management.base import BaseCommand

from api.models import Attendee, Event, Registration
from api.services.emails import send_save_the_date


class Command(BaseCommand):
    help = "Send save-the-date emails for a given event to all past attendees."

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            required=True,
            help="The ID of the upcoming event to announce.",
        )

    def handle(self, *args, **options):
        event_id = options["event_id"]
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Event with ID {event_id} not found."))
            return

        # Find all attendees who have a confirmed registration for any past event
        past_attendee_ids = (
            Registration.objects.filter(status="confirmed")
            .exclude(event=event)
            .values_list("attendee_id", flat=True)
            .distinct()
        )
        attendees = Attendee.objects.filter(id__in=past_attendee_ids)
        self.stdout.write(f"Found {attendees.count()} past attendee(s) to notify about '{event.title}'.")
        count = 0
        for attendee in attendees:
            send_save_the_date(attendee, event)
            count += 1
            self.stdout.write(f"  Sent save-the-date to {attendee.email}")
        self.stdout.write(self.style.SUCCESS(f"Done. Processed {count} attendee(s)."))
