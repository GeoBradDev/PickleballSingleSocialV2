from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Event


class Command(BaseCommand):
    help = "Close match forms and set events to completed for events that happened yesterday."

    def handle(self, *args, **options):
        yesterday = (timezone.now() - timedelta(days=1)).date()
        events = Event.objects.filter(
            event_date__date=yesterday,
            status__in=["open", "closed"],
        )
        self.stdout.write(f"Found {events.count()} event(s) from yesterday to complete.")
        for event in events:
            event.status = "completed"
            event.save()
            self.stdout.write(f"  Set event '{event.title}' to completed.")
        self.stdout.write(self.style.SUCCESS("Done."))
