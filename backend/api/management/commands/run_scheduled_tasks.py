import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger("api.commands.run_scheduled_tasks")


class Command(BaseCommand):
    help = "Dispatcher that runs all scheduled management commands with time-of-day gating."

    def handle(self, *args, **options):
        now = timezone.now()
        hour = now.hour
        verbosity = options["verbosity"]

        # Commands that run every hour
        always_commands = [
            "update_event_statuses",
            "expire_stale_registrations",
            "send_marketing_emails",
            "send_payment_reminders",
            "send_reminders",
            "send_save_the_date",
        ]

        # Time-windowed commands: (command_name, start_hour, end_hour)
        #
        # Timeline for a Saturday event:
        #   Saturday 7-9 AM:  send_dayof_reminders (confirmed attendees)
        #   Saturday evening: event happens (~3-5 PM)
        #   Saturday 8-10 PM: send_match_form (form links to confirmed attendees)
        #   Sunday 7-9 AM:    send_match_reminder (nudge non-submitters)
        #   Sunday 8-10 PM:   match pipeline (close form, process, notify)
        #
        windowed_commands = [
            ("send_dayof_reminders", 7, 9),
            ("send_match_form", 20, 22),
            ("send_match_reminder", 7, 9),
        ]

        # Match pipeline: runs 8-10 PM day after event
        # close_match_form transitions yesterday's events to "completed"
        # process_matches finds mutual selections
        # send_match_emails notifies matched pairs
        match_pipeline = [
            "close_match_form",
            "process_matches",
            "send_match_emails",
        ]
        match_pipeline_window = (20, 22)

        # Run always-on commands
        for cmd in always_commands:
            self._run_command(cmd, verbosity)

        # Run windowed commands
        for cmd, start, end in windowed_commands:
            if start <= hour < end:
                self._run_command(cmd, verbosity)
            elif verbosity >= 2:
                self.stdout.write(f"  Skipping {cmd}: outside window ({start}-{end}, current hour={hour})")

        # Run match pipeline
        start, end = match_pipeline_window
        if start <= hour < end:
            for cmd in match_pipeline:
                success = self._run_command(cmd, verbosity)
                if not success:
                    self.stderr.write(f"  Match pipeline halted: {cmd} failed, skipping remaining steps.")
                    break
        elif verbosity >= 2:
            self.stdout.write(f"  Skipping match pipeline: outside window ({start}-{end}, current hour={hour})")

    def _run_command(self, name, verbosity):
        """Run a management command, catching and logging exceptions.

        Returns True on success, False on failure.
        """
        if verbosity >= 2:
            self.stdout.write(f"Running {name}...")
        try:
            call_command(name)
            if verbosity >= 2:
                self.stdout.write(self.style.SUCCESS(f"  {name} completed."))
            return True
        except Exception:
            logger.exception("Command %s failed", name)
            self.stderr.write(self.style.ERROR(f"  {name} failed (see logs)."))
            return False
