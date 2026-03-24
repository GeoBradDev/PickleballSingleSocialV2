"""Unit tests for api.services.emails."""

from unittest.mock import patch

from django.test import TestCase

from api.models import EmailLog, Registration
from api.services.emails import (
    _already_sent,
    _log_email,
    render_marketing_email,
    send_dayof_reminder,
    send_match_form_link,
    send_match_form_reminder,
    send_match_notification,
    send_payment_expired,
    send_payment_reminder,
    send_registration_confirmation,
    send_reminder,
    send_save_the_date,
    send_waitlist_notification,
    send_waitlist_promotion,
)
from api.tests.helpers import make_attendee, make_event, make_match, make_registration


def _make_reg(event=None, attendee_n=1):
    """Create a registration and reload it with select_related."""
    event = event or make_event()
    attendee = make_attendee(n=attendee_n)
    reg = make_registration(event=event, attendee=attendee)
    return Registration.objects.select_related("attendee", "event").get(id=reg.id)


class RenderMarketingEmailTests(TestCase):
    """Tests for render_marketing_email."""

    def setUp(self):
        self.event = make_event()

    def test_normal_render_contains_event_details(self):
        subject, html = render_marketing_email("marketing_announcement", self.event)
        self.assertIn(self.event.age_label, subject)
        self.assertIn(self.event.age_label, html)
        self.assertIn(str(self.event.capacity), html)

    def test_full_render_spots_filling_uses_full_variant(self):
        normal_subject, normal_html = render_marketing_email(
            "marketing_spots_filling", self.event, full=False
        )
        full_subject, full_html = render_marketing_email(
            "marketing_spots_filling", self.event, full=True
        )
        self.assertNotEqual(normal_subject, full_subject)
        self.assertNotEqual(normal_html, full_html)
        self.assertIn("Sold Out", full_subject)

    def test_full_render_one_week_uses_full_variant(self):
        normal_subject, _ = render_marketing_email(
            "marketing_one_week", self.event, full=False
        )
        full_subject, full_html = render_marketing_email(
            "marketing_one_week", self.event, full=True
        )
        self.assertNotEqual(normal_subject, full_subject)
        self.assertIn("Waitlist Open", full_subject)

    def test_full_render_last_chance_uses_full_variant(self):
        normal_subject, _ = render_marketing_email(
            "marketing_last_chance", self.event, full=False
        )
        full_subject, full_html = render_marketing_email(
            "marketing_last_chance", self.event, full=True
        )
        self.assertNotEqual(normal_subject, full_subject)
        self.assertIn("Waitlist", full_subject)

    def test_full_render_announcement_falls_back_to_normal(self):
        normal_subject, normal_html = render_marketing_email(
            "marketing_announcement", self.event, full=False
        )
        full_subject, full_html = render_marketing_email(
            "marketing_announcement", self.event, full=True
        )
        self.assertEqual(normal_subject, full_subject)
        self.assertEqual(normal_html, full_html)


class AlreadySentAndLogEmailTests(TestCase):
    """Tests for _already_sent and _log_email."""

    def setUp(self):
        self.event = make_event()
        self.attendee = make_attendee(n=1)

    def test_already_sent_false_initially(self):
        self.assertFalse(_already_sent(self.attendee, self.event, "test_type"))

    def test_already_sent_true_after_log_email(self):
        _log_email(self.attendee, self.event, "test_type")
        self.assertTrue(_already_sent(self.attendee, self.event, "test_type"))

    def test_log_email_creates_email_log_record(self):
        _log_email(self.attendee, self.event, "test_type")
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=self.attendee,
                event=self.event,
                email_type="test_type",
            ).exists()
        )


SEND = "api.services.mailerlite.send_email"
ADD = "api.services.mailerlite.add_subscriber"


@patch(ADD)
@patch(SEND)
class SendRegistrationConfirmationTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send, mock_add):
        reg = _make_reg()
        send_registration_confirmation(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        mock_add.assert_called_once_with(
            reg.attendee.email, reg.attendee.first_name, reg.attendee.last_name
        )
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="registration_confirmation",
            ).exists()
        )

    def test_idempotent(self, mock_send, mock_add):
        reg = _make_reg()
        send_registration_confirmation(reg)
        mock_send.reset_mock()
        mock_add.reset_mock()
        send_registration_confirmation(reg)
        mock_send.assert_not_called()
        mock_add.assert_not_called()


@patch(ADD)
@patch(SEND)
class SendWaitlistNotificationTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send, mock_add):
        reg = _make_reg()
        send_waitlist_notification(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        mock_add.assert_called_once()
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="waitlist_notification",
            ).exists()
        )

    def test_idempotent(self, mock_send, mock_add):
        reg = _make_reg()
        send_waitlist_notification(reg)
        mock_send.reset_mock()
        send_waitlist_notification(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendWaitlistPromotionTests(TestCase):
    def test_sends_email_with_pay_url_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_waitlist_promotion(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        # The HTML body (third arg) should contain a pay URL with the registration id.
        html_body = mock_send.call_args[0][2]
        self.assertIn(f"registration={reg.id}", html_body)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="waitlist_promotion",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_waitlist_promotion(reg)
        mock_send.reset_mock()
        send_waitlist_promotion(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendPaymentExpiredTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_payment_expired(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="payment_expired",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_payment_expired(reg)
        mock_send.reset_mock()
        send_payment_expired(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendReminderTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_reminder(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="reminder",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_reminder(reg)
        mock_send.reset_mock()
        send_reminder(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendPaymentReminderTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_payment_reminder(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="payment_reminder",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_payment_reminder(reg)
        mock_send.reset_mock()
        send_payment_reminder(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendDayofReminderTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_dayof_reminder(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="dayof_reminder",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_dayof_reminder(reg)
        mock_send.reset_mock()
        send_dayof_reminder(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendMatchFormLinkTests(TestCase):
    def test_sends_email_with_match_url_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_match_form_link(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        html_body = mock_send.call_args[0][2]
        self.assertIn(str(reg.match_token), html_body)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="match_form",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_match_form_link(reg)
        mock_send.reset_mock()
        send_match_form_link(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendMatchFormReminderTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        reg = _make_reg()
        send_match_form_reminder(reg)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], reg.attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg.attendee,
                event=reg.event,
                email_type="match_form_reminder",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        reg = _make_reg()
        send_match_form_reminder(reg)
        mock_send.reset_mock()
        send_match_form_reminder(reg)
        mock_send.assert_not_called()


@patch(SEND)
class SendMatchNotificationTests(TestCase):
    def test_sends_to_both_parties_and_creates_two_logs(self, mock_send):
        event = make_event()
        reg_a = _make_reg(event=event, attendee_n=10)
        reg_b = _make_reg(event=event, attendee_n=11)
        match = make_match(event=event, reg_a=reg_a, reg_b=reg_b)
        send_match_notification(match)
        self.assertEqual(mock_send.call_count, 2)
        called_emails = {call[0][0] for call in mock_send.call_args_list}
        self.assertIn(reg_a.attendee.email, called_emails)
        self.assertIn(reg_b.attendee.email, called_emails)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg_a.attendee,
                event=event,
                email_type=f"match_notification_{reg_b.id}",
            ).exists()
        )
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=reg_b.attendee,
                event=event,
                email_type=f"match_notification_{reg_a.id}",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        event = make_event()
        reg_a = _make_reg(event=event, attendee_n=20)
        reg_b = _make_reg(event=event, attendee_n=21)
        match = make_match(event=event, reg_a=reg_a, reg_b=reg_b)
        send_match_notification(match)
        mock_send.reset_mock()
        send_match_notification(match)
        mock_send.assert_not_called()


@patch(SEND)
class SendSaveTheDateTests(TestCase):
    def test_sends_email_and_creates_log(self, mock_send):
        event = make_event()
        attendee = make_attendee(n=30)
        send_save_the_date(attendee, event)
        mock_send.assert_called_once()
        self.assertEqual(mock_send.call_args[0][0], attendee.email)
        self.assertTrue(
            EmailLog.objects.filter(
                attendee=attendee,
                event=event,
                email_type="save_the_date",
            ).exists()
        )

    def test_idempotent(self, mock_send):
        event = make_event()
        attendee = make_attendee(n=31)
        send_save_the_date(attendee, event)
        mock_send.reset_mock()
        send_save_the_date(attendee, event)
        mock_send.assert_not_called()
