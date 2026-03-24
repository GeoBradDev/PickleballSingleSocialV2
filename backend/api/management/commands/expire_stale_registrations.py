import logging
from datetime import timedelta

import stripe
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Registration
from api.views import _try_promote_waitlisted

logger = logging.getLogger("api.commands")

DEFAULT_HOURS = 24


class Command(BaseCommand):
    help = "Cancel Stripe PaymentIntents and expire registrations that have been pending too long."

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=DEFAULT_HOURS,
            help=f"Expire registrations pending longer than this many hours (default: {DEFAULT_HOURS})",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Log what would be expired without making changes",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(hours=hours)

        stale = (
            Registration.objects.filter(status="pending", created_at__lt=cutoff)
            .exclude(payment_intent_id="")
            .select_related("attendee", "event")
        )

        count = stale.count()
        if count == 0:
            self.stdout.write("No stale pending registrations found.")
            return

        self.stdout.write(f"Found {count} stale pending registration(s) older than {hours}h.")

        stripe.api_key = settings.STRIPE_SECRET_KEY

        for reg in stale:
            if dry_run:
                self.stdout.write(
                    f"  [DRY RUN] Would expire registration {reg.id}: {reg.attendee.email} for {reg.event.title}"
                )
                continue

            # Cancel the PaymentIntent in Stripe
            try:
                stripe.PaymentIntent.cancel(reg.payment_intent_id)
            except stripe.error.InvalidRequestError:
                # Already canceled or in a non-cancelable state
                pass

            reg.status = "expired"
            reg.save()
            logger.info(
                "Expired registration %d: %s for %s",
                reg.id,
                reg.attendee.email,
                reg.event.title,
            )

            from api.services.emails import send_payment_expired

            send_payment_expired(reg)

            # Promote next waitlisted person of same gender
            _try_promote_waitlisted(reg.event, reg.attendee.gender)

        self.stdout.write(self.style.SUCCESS(f"Expired {count} registration(s)."))
