import logging

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event

logger = logging.getLogger("api.commands.close_match_form")


class Command(BaseCommand):
    help = "Close match forms by setting events from yesterday to completed status."

    def handle(self, *args, **options):
        yesterday = (timezone.now() - timedelta(days=1)).date()
        events = Event.objects.filter(
            event_date__date=yesterday,
            status="closed",
        )
        count = events.count()
        self.stdout.write(f"Found {count} closed event(s) from yesterday to complete.")
        for event in events:
            event.status = "completed"
            event.save(update_fields=["status"])
            logger.info("Match form closed, event %d completed: %s", event.id, event.title)
            self.stdout.write(f"  Set event '{event.title}' to completed.")
        self.stdout.write(self.style.SUCCESS("Done."))
