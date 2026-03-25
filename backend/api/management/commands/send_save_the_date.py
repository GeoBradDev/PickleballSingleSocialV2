from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Attendee, EmailLog, Event, Registration
from api.services.emails import send_save_the_date


class Command(BaseCommand):
    help = "Send save-the-date emails for a given event to all past attendees."

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            required=False,
            help="The ID of the upcoming event to announce. If omitted, auto-detects the next open event.",
        )

    def handle(self, *args, **options):
        event_id = options["event_id"]

        if event_id:
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Event with ID {event_id} not found."))
                return
        else:
            event = Event.objects.filter(status="open", event_date__gt=timezone.now()).order_by("event_date").first()
            if not event:
                if options["verbosity"] >= 2:
                    self.stdout.write("No upcoming open events found.")
                return

            has_any_sent = EmailLog.objects.filter(event=event, email_type="save_the_date").exists()
            if has_any_sent:
                if options["verbosity"] >= 2:
                    self.stdout.write(
                        f"Save-the-dates already sent for '{event.title}', "
                        f"skipping auto-detect (use --event-id to force)."
                    )
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
