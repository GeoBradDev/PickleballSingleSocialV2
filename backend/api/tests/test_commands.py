"""Unit tests for management commands."""

from datetime import timedelta
from io import StringIO
from unittest.mock import MagicMock, patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from api.models import MarketingEmailLog, Match, MatchSubmission, Registration
from api.tests.helpers import (
    make_attendee,
    make_event,
    make_match,
    make_registration,
    make_submission,
)


# ---------------------------------------------------------------------------
# 1. close_match_form
# ---------------------------------------------------------------------------
class CloseMatchFormTests(TestCase):
    def test_open_event_yesterday_set_to_completed(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="open")
        out = StringIO()
        call_command("close_match_form", stdout=out)
        event.refresh_from_db()
        self.assertEqual(event.status, "completed")
        self.assertIn("completed", out.getvalue())

    def test_closed_event_yesterday_set_to_completed(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="closed")
        out = StringIO()
        call_command("close_match_form", stdout=out)
        event.refresh_from_db()
        self.assertEqual(event.status, "completed")

    def test_event_today_not_affected(self):
        event = make_event(event_date=timezone.now(), status="open")
        out = StringIO()
        call_command("close_match_form", stdout=out)
        event.refresh_from_db()
        self.assertEqual(event.status, "open")

    def test_already_completed_not_affected(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        out = StringIO()
        call_command("close_match_form", stdout=out)
        event.refresh_from_db()
        self.assertEqual(event.status, "completed")
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 2. process_matches
# ---------------------------------------------------------------------------
class ProcessMatchesTests(TestCase):
    def test_mutual_selections_create_match(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        reg_a = make_registration(event=event, attendee=make_attendee(1))
        reg_b = make_registration(event=event, attendee=make_attendee(2))

        # Both select each other
        make_submission(event, reg_a, selected_regs=[reg_b])
        make_submission(event, reg_b, selected_regs=[reg_a])

        out = StringIO()
        call_command("process_matches", stdout=out)

        self.assertEqual(Match.objects.filter(event=event).count(), 1)
        self.assertIn("Created match", out.getvalue())

    def test_no_mutual_selections_no_match(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        reg_a = make_registration(event=event, attendee=make_attendee(1))
        reg_b = make_registration(event=event, attendee=make_attendee(2))

        # Only reg_a selects reg_b, but not the reverse
        make_submission(event, reg_a, selected_regs=[reg_b])
        make_submission(event, reg_b, selected_regs=[])

        out = StringIO()
        call_command("process_matches", stdout=out)

        self.assertEqual(Match.objects.filter(event=event).count(), 0)
        self.assertIn("Created 0", out.getvalue())

    def test_event_with_existing_matches_skipped(self):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        reg_a = make_registration(event=event, attendee=make_attendee(1))
        reg_b = make_registration(event=event, attendee=make_attendee(2))

        # Create an existing match so the event is excluded
        make_match(event, reg_a, reg_b)

        # Also add mutual submissions
        make_submission(event, reg_a, selected_regs=[reg_b])
        make_submission(event, reg_b, selected_regs=[reg_a])

        out = StringIO()
        call_command("process_matches", stdout=out)

        # Should still be only the original match
        self.assertEqual(Match.objects.filter(event=event).count(), 1)
        self.assertIn("Found 0", out.getvalue())

    def test_no_completed_events(self):
        make_event(status="open")
        out = StringIO()
        call_command("process_matches", stdout=out)
        self.assertEqual(Match.objects.count(), 0)
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 3. send_match_emails
# ---------------------------------------------------------------------------
class SendMatchEmailsTests(TestCase):
    @patch("api.management.commands.send_match_emails.send_match_notification")
    def test_unnotified_match_sends_notification(self, mock_notify):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        reg_a = make_registration(event=event, attendee=make_attendee(1))
        reg_b = make_registration(event=event, attendee=make_attendee(2))
        match = make_match(event, reg_a, reg_b, notified=False)

        out = StringIO()
        call_command("send_match_emails", stdout=out)

        mock_notify.assert_called_once_with(match)
        match.refresh_from_db()
        self.assertTrue(match.notified)

    @patch("api.management.commands.send_match_emails.send_match_notification")
    def test_already_notified_match_skipped(self, mock_notify):
        yesterday = timezone.now() - timedelta(days=1)
        event = make_event(event_date=yesterday, status="completed")
        reg_a = make_registration(event=event, attendee=make_attendee(1))
        reg_b = make_registration(event=event, attendee=make_attendee(2))
        make_match(event, reg_a, reg_b, notified=True)

        out = StringIO()
        call_command("send_match_emails", stdout=out)

        mock_notify.assert_not_called()
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 4. send_match_form
# ---------------------------------------------------------------------------
class SendMatchFormTests(TestCase):
    @patch("api.management.commands.send_match_form.send_match_form_link")
    def test_event_today_sends_links(self, mock_send):
        event = make_event(event_date=timezone.now(), status="open")
        reg = make_registration(event=event, attendee=make_attendee(1), status="confirmed")

        out = StringIO()
        call_command("send_match_form", stdout=out)

        mock_send.assert_called_once_with(reg)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_match_form.send_match_form_link")
    def test_no_events_today(self, mock_send):
        tomorrow = timezone.now() + timedelta(days=1)
        make_event(event_date=tomorrow, status="open")

        out = StringIO()
        call_command("send_match_form", stdout=out)

        mock_send.assert_not_called()
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 5. send_match_reminder
# ---------------------------------------------------------------------------
class SendMatchReminderTests(TestCase):
    @patch("api.management.commands.send_match_reminder.send_match_form_reminder")
    def test_confirmed_without_submission_gets_reminder(self, mock_send):
        event = make_event(event_date=timezone.now(), status="open")
        reg = make_registration(event=event, attendee=make_attendee(1), status="confirmed")

        out = StringIO()
        call_command("send_match_reminder", stdout=out)

        mock_send.assert_called_once_with(reg)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_match_reminder.send_match_form_reminder")
    def test_registration_with_submission_skipped(self, mock_send):
        event = make_event(event_date=timezone.now(), status="open")
        reg = make_registration(event=event, attendee=make_attendee(1), status="confirmed")
        make_submission(event, reg, selected_regs=[])

        out = StringIO()
        call_command("send_match_reminder", stdout=out)

        mock_send.assert_not_called()
        self.assertIn("Processed 0", out.getvalue())


# ---------------------------------------------------------------------------
# 6. send_dayof_reminders
# ---------------------------------------------------------------------------
class SendDayofRemindersTests(TestCase):
    @patch("api.management.commands.send_dayof_reminders.send_dayof_reminder")
    def test_event_today_sends_reminders(self, mock_send):
        event = make_event(event_date=timezone.now(), status="open")
        reg = make_registration(event=event, attendee=make_attendee(1), status="confirmed")

        out = StringIO()
        call_command("send_dayof_reminders", stdout=out)

        mock_send.assert_called_once_with(reg)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_dayof_reminders.send_dayof_reminder")
    def test_no_events_today(self, mock_send):
        tomorrow = timezone.now() + timedelta(days=1)
        make_event(event_date=tomorrow, status="open")

        out = StringIO()
        call_command("send_dayof_reminders", stdout=out)

        mock_send.assert_not_called()
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 7. send_reminders
# ---------------------------------------------------------------------------
class SendRemindersTests(TestCase):
    @patch("api.management.commands.send_reminders.send_reminder")
    def test_event_within_3_days_sends_reminders(self, mock_send):
        event = make_event(
            event_date=timezone.now() + timedelta(days=2),
            status="open",
        )
        reg = make_registration(event=event, attendee=make_attendee(1), status="confirmed")

        out = StringIO()
        call_command("send_reminders", stdout=out)

        mock_send.assert_called_once_with(reg)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_reminders.send_reminder")
    def test_event_more_than_3_days_away_skipped(self, mock_send):
        make_event(
            event_date=timezone.now() + timedelta(days=5),
            status="open",
        )

        out = StringIO()
        call_command("send_reminders", stdout=out)

        mock_send.assert_not_called()
        self.assertIn("Found 0", out.getvalue())


# ---------------------------------------------------------------------------
# 8. send_payment_reminders
# ---------------------------------------------------------------------------
class SendPaymentRemindersTests(TestCase):
    @patch("api.management.commands.send_payment_reminders.send_payment_reminder")
    def test_pending_registration_gets_reminder(self, mock_send):
        event = make_event(status="open")
        reg = make_registration(
            event=event,
            attendee=make_attendee(1),
            status="pending",
        )

        out = StringIO()
        call_command("send_payment_reminders", stdout=out)

        mock_send.assert_called_once_with(reg)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_payment_reminders.send_payment_reminder")
    def test_confirmed_registration_skipped(self, mock_send):
        event = make_event(status="open")
        make_registration(
            event=event,
            attendee=make_attendee(1),
            status="confirmed",
        )

        out = StringIO()
        call_command("send_payment_reminders", stdout=out)

        mock_send.assert_not_called()
        self.assertIn("Processed 0", out.getvalue())


# ---------------------------------------------------------------------------
# 9. expire_stale_registrations
# ---------------------------------------------------------------------------
class ExpireStaleRegistrationsTests(TestCase):
    @patch("api.management.commands.expire_stale_registrations._try_promote_waitlisted")
    @patch("api.management.commands.expire_stale_registrations.stripe.PaymentIntent.cancel")
    @patch("api.services.emails.send_payment_expired")
    def test_stale_pending_registration_expired(
        self, mock_send_expired, mock_cancel, mock_promote
    ):
        event = make_event(status="open")
        attendee = make_attendee(1)
        reg = make_registration(
            event=event,
            attendee=attendee,
            status="pending",
            payment_intent_id="pi_stale123",
        )
        # Force created_at to be >24h ago
        Registration.objects.filter(pk=reg.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )

        out = StringIO()
        call_command("expire_stale_registrations", stdout=out)

        reg.refresh_from_db()
        self.assertEqual(reg.status, "expired")
        mock_cancel.assert_called_once_with("pi_stale123")
        mock_promote.assert_called_once_with(event, attendee.gender)

    @patch("api.management.commands.expire_stale_registrations._try_promote_waitlisted")
    @patch("api.management.commands.expire_stale_registrations.stripe.PaymentIntent.cancel")
    @patch("api.services.emails.send_payment_expired")
    def test_recent_pending_registration_not_affected(
        self, mock_send_expired, mock_cancel, mock_promote
    ):
        event = make_event(status="open")
        reg = make_registration(
            event=event,
            attendee=make_attendee(1),
            status="pending",
            payment_intent_id="pi_recent",
        )

        out = StringIO()
        call_command("expire_stale_registrations", stdout=out)

        reg.refresh_from_db()
        self.assertEqual(reg.status, "pending")
        mock_cancel.assert_not_called()
        self.assertIn("No stale", out.getvalue())

    @patch("api.management.commands.expire_stale_registrations._try_promote_waitlisted")
    @patch("api.management.commands.expire_stale_registrations.stripe.PaymentIntent.cancel")
    @patch("api.services.emails.send_payment_expired")
    def test_dry_run_does_not_change_status(
        self, mock_send_expired, mock_cancel, mock_promote
    ):
        event = make_event(status="open")
        reg = make_registration(
            event=event,
            attendee=make_attendee(1),
            status="pending",
            payment_intent_id="pi_dry",
        )
        Registration.objects.filter(pk=reg.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )

        out = StringIO()
        call_command("expire_stale_registrations", "--dry-run", stdout=out)

        reg.refresh_from_db()
        self.assertEqual(reg.status, "pending")
        mock_cancel.assert_not_called()
        self.assertIn("DRY RUN", out.getvalue())


# ---------------------------------------------------------------------------
# 10. send_marketing_emails
# ---------------------------------------------------------------------------
class SendMarketingEmailsTests(TestCase):
    @patch("api.management.commands.send_marketing_emails.create_campaign")
    @patch("api.management.commands.send_marketing_emails.get_total_subscriber_count", return_value=100)
    @patch("api.management.commands.send_marketing_emails.render_marketing_email")
    def test_open_event_14_days_away_sends_spots_filling(
        self, mock_render, mock_count, mock_campaign
    ):
        event = make_event(
            event_date=timezone.now() + timedelta(days=14),
            status="open",
        )
        mock_render.return_value = ("Subject", "<html>body</html>")
        mock_campaign.return_value = {"id": "camp_1"}

        out = StringIO()
        call_command("send_marketing_emails", stdout=out)

        self.assertTrue(mock_campaign.called)
        self.assertTrue(
            MarketingEmailLog.objects.filter(event=event).exists()
        )

    @patch("api.management.commands.send_marketing_emails.create_campaign")
    @patch("api.management.commands.send_marketing_emails.get_total_subscriber_count", return_value=100)
    @patch("api.management.commands.send_marketing_emails.render_marketing_email")
    def test_already_sent_skipped(self, mock_render, mock_count, mock_campaign):
        event = make_event(
            event_date=timezone.now() + timedelta(days=14),
            status="open",
        )
        # Pre-populate logs for all emails that would fire at <=14 days
        for key in ("marketing_spots_filling", "marketing_one_week", "marketing_last_chance"):
            MarketingEmailLog.objects.create(
                event=event, email_key=key, subscriber_count=100
            )
        # Also mark the earlier ones that would match (days_until <= days_before)
        for key in ("marketing_announcement", "marketing_registration_open"):
            MarketingEmailLog.objects.create(
                event=event, email_key=key, subscriber_count=100
            )

        out = StringIO()
        call_command("send_marketing_emails", "--verbosity=2", stdout=out)

        mock_campaign.assert_not_called()

    @patch("api.management.commands.send_marketing_emails.create_campaign")
    @patch("api.management.commands.send_marketing_emails.get_total_subscriber_count", return_value=100)
    @patch("api.management.commands.send_marketing_emails.render_marketing_email")
    def test_no_open_events(self, mock_render, mock_count, mock_campaign):
        # Only a closed event
        make_event(
            event_date=timezone.now() + timedelta(days=14),
            status="closed",
        )

        out = StringIO()
        call_command("send_marketing_emails", "--verbosity=2", stdout=out)

        mock_campaign.assert_not_called()


# ---------------------------------------------------------------------------
# 11. send_save_the_date
# ---------------------------------------------------------------------------
class SendSaveTheDateTests(TestCase):
    @patch("api.management.commands.send_save_the_date.send_save_the_date")
    def test_sends_to_past_attendees(self, mock_send):
        # Create a past event with a confirmed registration
        past_event = make_event(
            event_date=timezone.now() - timedelta(days=30),
            status="completed",
        )
        past_attendee = make_attendee(1)
        make_registration(event=past_event, attendee=past_attendee, status="confirmed")

        # Create the new event to announce
        new_event = make_event(
            event_date=timezone.now() + timedelta(days=14),
            status="open",
        )

        out = StringIO()
        call_command("send_save_the_date", f"--event-id={new_event.id}", stdout=out)

        mock_send.assert_called_once_with(past_attendee, new_event)
        self.assertIn("Processed 1", out.getvalue())

    @patch("api.management.commands.send_save_the_date.send_save_the_date")
    def test_event_not_found_shows_error(self, mock_send):
        out = StringIO()
        err = StringIO()
        call_command("send_save_the_date", "--event-id=99999", stdout=out, stderr=err)

        mock_send.assert_not_called()
        self.assertIn("not found", err.getvalue())
