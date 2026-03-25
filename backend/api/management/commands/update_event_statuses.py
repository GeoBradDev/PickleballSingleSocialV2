import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event

logger = logging.getLogger("api.commands.update_event_statuses")


class Command(BaseCommand):
    help = "Automatically transition event statuses based on date."

    def handle(self, *args, **options):
        now = timezone.now()
        verbosity = options["verbosity"]
        changed = False

        # Close open events whose date has passed
        open_past = list(Event.objects.filter(status="open", event_date__lt=now))
        if open_past:
            for event in open_past:
                event.status = "closed"
                event.save(update_fields=["status"])
                logger.info("Event %d auto-closed: %s", event.id, event.title)
            if verbosity >= 1:
                self.stdout.write(self.style.SUCCESS(f"Closed {len(open_past)} past event(s)."))
            changed = True

        # Move closed events to completed (1-day buffer for match form submissions)
        one_day_ago = now - timezone.timedelta(days=1)
        closed_past = list(Event.objects.filter(status="closed", event_date__lt=one_day_ago))
        if closed_past:
            for event in closed_past:
                event.status = "completed"
                event.save(update_fields=["status"])
                logger.info("Event %d auto-completed: %s", event.id, event.title)
            if verbosity >= 1:
                self.stdout.write(self.style.SUCCESS(f"Completed {len(closed_past)} event(s)."))
            changed = True

        # Open the next draft event if no event is currently open
        has_open = Event.objects.filter(status="open").exists()
        if not has_open:
            next_draft = Event.objects.filter(status="draft", event_date__gt=now).order_by("event_date").first()
            if next_draft:
                next_draft.status = "open"
                next_draft.save(update_fields=["status"])
                logger.info("Event %d auto-opened: %s", next_draft.id, next_draft.title)
                if verbosity >= 1:
                    self.stdout.write(self.style.SUCCESS(f"Opened next event: {next_draft.title}"))
                changed = True

        if not changed and verbosity >= 2:
            self.stdout.write("No status changes needed.")
