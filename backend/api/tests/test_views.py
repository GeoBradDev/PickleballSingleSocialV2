"""Unit tests for api.views -- Django Ninja endpoints."""

import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from api.models import Attendee, Event, Match, MatchSubmission, Registration
from api.tests.helpers import (
    make_attendee,
    make_event,
    make_match,
    make_registration,
    make_submission,
)
from api.views import _check_capacity, _get_price_cents


# ---------------------------------------------------------------------------
# Helper constants
# ---------------------------------------------------------------------------

REG_PAYLOAD = {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane@example.com",
    "phone": "555-123-4567",
    "gender": "female",
    "age": 30,
    "experience": "beginner",
    "attending_coaching": True,
    "attending_happy_hour": False,
}

MAILERLITE_ADD = "api.services.mailerlite.add_subscriber"
MAILERLITE_SEND = "api.services.mailerlite.send_email"
STRIPE_PI_CREATE = "stripe.PaymentIntent.create"
STRIPE_PI_RETRIEVE = "stripe.PaymentIntent.retrieve"
STRIPE_WEBHOOK_CONSTRUCT = "stripe.Webhook.construct_event"
EMAIL_CONFIRMATION = "api.services.emails.send_registration_confirmation"
EMAIL_WAITLIST = "api.services.emails.send_waitlist_notification"
EMAIL_PROMOTION = "api.services.emails.send_waitlist_promotion"
EMAIL_EXPIRED = "api.services.emails.send_payment_expired"


def _stripe_create_mock():
    return MagicMock(id="pi_test", client_secret="cs_test")


def _stripe_retrieve_mock():
    return MagicMock(client_secret="cs_test")


# ============================================================================
# 1. GET /api/events/  --  list open events
# ============================================================================


class ListEventsTest(TestCase):
    def test_returns_open_events_only(self):
        make_event(status="open")
        make_event(status="draft")
        make_event(status="closed")
        make_event(status="completed")

        resp = self.client.get("/api/events/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "open")

    def test_empty_when_no_open(self):
        make_event(status="draft")
        resp = self.client.get("/api/events/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])


# ============================================================================
# 2. GET /api/events/{id}/  --  get single event
# ============================================================================


class GetEventTest(TestCase):
    def test_found(self):
        event = make_event()
        resp = self.client.get(f"/api/events/{event.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], event.id)

    def test_not_found(self):
        resp = self.client.get("/api/events/99999/")
        self.assertEqual(resp.status_code, 404)
        self.assertIn("not found", resp.json()["detail"].lower())


# ============================================================================
# 3. POST /api/events/{id}/register/  --  registration
# ============================================================================


@override_settings(
    STRIPE_SECRET_KEY="sk_test",
    STRIPE_WEBHOOK_SECRET="whsec_test",
    MAILERLITE_AGE_GROUPS={"25-45": "grp_123"},
)
class RegisterForEventTest(TestCase):
    def setUp(self):
        self.event = make_event(status="open", capacity=32, min_age=25, max_age=45)

    # --- successful registration ---
    @patch(EMAIL_WAITLIST)
    @patch(MAILERLITE_ADD)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    def test_successful_registration(self, mock_stripe, mock_ml, mock_wl_email):
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(REG_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "pending")
        self.assertEqual(body["client_secret"], "cs_test")
        self.assertIn("registration_id", body)
        mock_stripe.assert_called_once()
        mock_ml.assert_called_once()

    # --- event not found ---
    @patch(MAILERLITE_ADD)
    def test_event_not_found(self, mock_ml):
        resp = self.client.post(
            "/api/events/99999/register/",
            data=json.dumps(REG_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    # --- age too young ---
    @patch(MAILERLITE_ADD)
    def test_age_too_young(self, mock_ml):
        payload = {**REG_PAYLOAD, "age": 20}
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ages", resp.json()["detail"].lower())

    # --- age too old ---
    @patch(MAILERLITE_ADD)
    def test_age_too_old(self, mock_ml):
        payload = {**REG_PAYLOAD, "age": 50}
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ages", resp.json()["detail"].lower())

    # --- age validation with no max_age ---
    @patch(MAILERLITE_ADD)
    def test_age_too_young_no_max(self, mock_ml):
        event = make_event(min_age=30, max_age=None)
        payload = {**REG_PAYLOAD, "age": 25, "email": "young@example.com"}
        resp = self.client.post(
            f"/api/events/{event.id}/register/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("older", resp.json()["detail"].lower())

    # --- duplicate: already confirmed ---
    @patch(MAILERLITE_ADD)
    def test_duplicate_confirmed(self, mock_ml):
        attendee = make_attendee(
            first_name="Jane", last_name="Doe", email="jane@example.com",
            gender="female", age=30,
        )
        make_registration(event=self.event, attendee=attendee, status="confirmed")
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(REG_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("already registered", resp.json()["detail"].lower())

    # --- duplicate: already waitlisted ---
    @patch(MAILERLITE_ADD)
    def test_duplicate_waitlisted(self, mock_ml):
        attendee = make_attendee(
            first_name="Jane", last_name="Doe", email="jane@example.com",
            gender="female", age=30,
        )
        make_registration(event=self.event, attendee=attendee, status="waitlisted")
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(payload := REG_PAYLOAD.copy()),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "waitlisted")

    # --- duplicate: pending with existing payment intent ---
    @patch(MAILERLITE_ADD)
    @patch(STRIPE_PI_RETRIEVE, return_value=_stripe_retrieve_mock())
    def test_duplicate_pending_with_intent(self, mock_retrieve, mock_ml):
        attendee = make_attendee(
            first_name="Jane", last_name="Doe", email="jane@example.com",
            gender="female", age=30,
        )
        make_registration(
            event=self.event, attendee=attendee,
            status="pending", payment_intent_id="pi_existing",
        )
        resp = self.client.post(
            f"/api/events/{self.event.id}/register/",
            data=json.dumps(REG_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["status"], "pending")
        self.assertEqual(body["client_secret"], "cs_test")
        mock_retrieve.assert_called_once_with("pi_existing")

    # --- capacity full -> waitlisted ---
    @patch(EMAIL_WAITLIST)
    @patch(MAILERLITE_ADD)
    def test_capacity_full_waitlisted(self, mock_ml, mock_wl_email):
        event = make_event(capacity=1, status="open")
        # Fill the single spot
        a1 = make_attendee(n=10, gender="female")
        make_registration(event=event, attendee=a1, status="confirmed")

        resp = self.client.post(
            f"/api/events/{event.id}/register/",
            data=json.dumps(REG_PAYLOAD),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "waitlisted")
        mock_wl_email.assert_called_once()

    # --- male ratio exceeded -> waitlisted ---
    @patch(EMAIL_WAITLIST)
    @patch(MAILERLITE_ADD)
    def test_male_ratio_exceeded_waitlisted(self, mock_ml, mock_wl_email):
        # capacity=2, max_male_ratio=0.5 => at most 1 male in 2 spots
        event = make_event(capacity=10, max_male_ratio=0.5, status="open")
        # Already have 1 male pending
        m1 = make_attendee(n=20, gender="male")
        make_registration(event=event, attendee=m1, status="pending")

        male_payload = {**REG_PAYLOAD, "gender": "male", "email": "john@example.com"}
        resp = self.client.post(
            f"/api/events/{event.id}/register/",
            data=json.dumps(male_payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "waitlisted")


# ============================================================================
# 4. _get_price_cents
# ============================================================================


class GetPriceCentsTest(TestCase):
    def test_female_price(self):
        self.assertEqual(_get_price_cents("female"), 1500)

    def test_male_price(self):
        self.assertEqual(_get_price_cents("male"), 2000)

    def test_other_defaults_to_male(self):
        self.assertEqual(_get_price_cents("other"), 2000)


# ============================================================================
# 5. _check_capacity
# ============================================================================


class CheckCapacityTest(TestCase):
    def test_under_capacity(self):
        event = make_event(capacity=10)
        self.assertTrue(_check_capacity(event, "female"))

    def test_at_capacity(self):
        event = make_event(capacity=1)
        a = make_attendee(n=50, gender="female")
        make_registration(event=event, attendee=a, status="confirmed")
        self.assertFalse(_check_capacity(event, "female"))

    def test_male_ratio_exceeded(self):
        event = make_event(capacity=10, max_male_ratio=0.5)
        # One male pending already
        m = make_attendee(n=51, gender="male")
        make_registration(event=event, attendee=m, status="pending")
        # Adding another male would be 2/2 = 1.0 > 0.5
        self.assertFalse(_check_capacity(event, "male"))

    def test_female_not_limited_by_ratio(self):
        event = make_event(capacity=10, max_male_ratio=0.5)
        m = make_attendee(n=52, gender="male")
        make_registration(event=event, attendee=m, status="pending")
        # Female should still be allowed
        self.assertTrue(_check_capacity(event, "female"))


# ============================================================================
# 6. stripe_webhook
# ============================================================================


@override_settings(STRIPE_WEBHOOK_SECRET="whsec_test")
class StripeWebhookTest(TestCase):
    url = "/api/webhooks/stripe/"

    @patch(EMAIL_CONFIRMATION)
    @patch(STRIPE_WEBHOOK_CONSTRUCT)
    def test_payment_intent_succeeded(self, mock_construct, mock_email):
        event = make_event()
        attendee = make_attendee(n=60)
        reg = make_registration(event=event, attendee=attendee, status="pending")
        mock_construct.return_value = {
            "type": "payment_intent.succeeded",
            "data": {
                "object": {
                    "metadata": {"registration_id": str(reg.id)},
                },
            },
        }
        resp = self.client.post(
            self.url, data=b'{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(resp.status_code, 200)
        reg.refresh_from_db()
        self.assertEqual(reg.status, "confirmed")
        mock_email.assert_called_once()

    @patch(EMAIL_EXPIRED)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    @patch(STRIPE_WEBHOOK_CONSTRUCT)
    def test_payment_intent_canceled(self, mock_construct, mock_stripe_create, mock_email):
        event = make_event()
        attendee = make_attendee(n=61)
        reg = make_registration(event=event, attendee=attendee, status="pending")
        mock_construct.return_value = {
            "type": "payment_intent.canceled",
            "data": {
                "object": {
                    "metadata": {"registration_id": str(reg.id)},
                },
            },
        }
        resp = self.client.post(
            self.url, data=b'{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(resp.status_code, 200)
        reg.refresh_from_db()
        self.assertEqual(reg.status, "expired")

    @patch(STRIPE_WEBHOOK_CONSTRUCT, side_effect=ValueError("bad payload"))
    def test_invalid_payload(self, mock_construct):
        resp = self.client.post(
            self.url, data=b'bad', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid payload", resp.content.decode())

    @patch(STRIPE_WEBHOOK_CONSTRUCT, side_effect=__import__("stripe").error.SignatureVerificationError("bad sig", "sig"))
    def test_invalid_signature(self, mock_construct):
        resp = self.client.post(
            self.url, data=b'{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="badsig",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Invalid signature", resp.content.decode())


# ============================================================================
# 7. _handle_payment_succeeded
# ============================================================================


class HandlePaymentSucceededTest(TestCase):
    @patch(EMAIL_CONFIRMATION)
    def test_missing_registration_id(self, mock_email):
        from api.views import _handle_payment_succeeded

        _handle_payment_succeeded({"metadata": {}})
        mock_email.assert_not_called()

    @patch(EMAIL_CONFIRMATION)
    def test_registration_not_found(self, mock_email):
        from api.views import _handle_payment_succeeded

        _handle_payment_succeeded({"metadata": {"registration_id": "99999"}})
        mock_email.assert_not_called()

    @patch(EMAIL_CONFIRMATION)
    def test_already_confirmed_idempotent(self, mock_email):
        from api.views import _handle_payment_succeeded

        event = make_event()
        attendee = make_attendee(n=70)
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        _handle_payment_succeeded({"metadata": {"registration_id": str(reg.id)}})
        reg.refresh_from_db()
        self.assertEqual(reg.status, "confirmed")
        mock_email.assert_not_called()

    @patch(EMAIL_CONFIRMATION)
    def test_normal_flow(self, mock_email):
        from api.views import _handle_payment_succeeded

        event = make_event()
        attendee = make_attendee(n=71)
        reg = make_registration(event=event, attendee=attendee, status="pending")
        _handle_payment_succeeded({"metadata": {"registration_id": str(reg.id)}})
        reg.refresh_from_db()
        self.assertEqual(reg.status, "confirmed")
        mock_email.assert_called_once()


# ============================================================================
# 8. _handle_payment_canceled
# ============================================================================


class HandlePaymentCanceledTest(TestCase):
    @patch(EMAIL_EXPIRED)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    def test_normal_flow(self, mock_stripe, mock_email):
        from api.views import _handle_payment_canceled

        event = make_event()
        attendee = make_attendee(n=80)
        reg = make_registration(event=event, attendee=attendee, status="pending")
        _handle_payment_canceled({"metadata": {"registration_id": str(reg.id)}})
        reg.refresh_from_db()
        self.assertEqual(reg.status, "expired")
        mock_email.assert_called_once()

    @patch(EMAIL_EXPIRED)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    def test_already_non_pending(self, mock_stripe, mock_email):
        from api.views import _handle_payment_canceled

        event = make_event()
        attendee = make_attendee(n=81)
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        _handle_payment_canceled({"metadata": {"registration_id": str(reg.id)}})
        reg.refresh_from_db()
        # Should remain confirmed, not changed
        self.assertEqual(reg.status, "confirmed")
        mock_email.assert_not_called()

    def test_missing_registration_id(self):
        from api.views import _handle_payment_canceled

        # Should not raise
        _handle_payment_canceled({"metadata": {}})

    def test_registration_not_found(self):
        from api.views import _handle_payment_canceled

        _handle_payment_canceled({"metadata": {"registration_id": "99999"}})


# ============================================================================
# 9. _try_promote_waitlisted
# ============================================================================


@override_settings(STRIPE_SECRET_KEY="sk_test")
class TryPromoteWaitlistedTest(TestCase):
    @patch(EMAIL_PROMOTION)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    def test_no_waitlisted(self, mock_stripe, mock_email):
        from api.views import _try_promote_waitlisted

        event = make_event()
        _try_promote_waitlisted(event, "female")
        mock_stripe.assert_not_called()
        mock_email.assert_not_called()

    @patch(EMAIL_PROMOTION)
    @patch(STRIPE_PI_CREATE, return_value=_stripe_create_mock())
    def test_promote_successfully(self, mock_stripe, mock_email):
        from api.views import _try_promote_waitlisted

        event = make_event(capacity=10)
        attendee = make_attendee(n=90, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="waitlisted")

        _try_promote_waitlisted(event, "female")

        reg.refresh_from_db()
        self.assertEqual(reg.status, "pending")
        self.assertEqual(reg.payment_intent_id, "pi_test")
        mock_stripe.assert_called_once()
        mock_email.assert_called_once()


# ============================================================================
# 10. GET /api/registrations/{id}/payment/
# ============================================================================


@override_settings(STRIPE_SECRET_KEY="sk_test")
class GetRegistrationPaymentTest(TestCase):
    @patch(STRIPE_PI_RETRIEVE, return_value=_stripe_retrieve_mock())
    def test_pending_with_intent(self, mock_retrieve):
        event = make_event()
        attendee = make_attendee(n=100, gender="female")
        reg = make_registration(
            event=event, attendee=attendee,
            status="pending", payment_intent_id="pi_abc",
        )
        resp = self.client.get(f"/api/registrations/{reg.id}/payment/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["client_secret"], "cs_test")
        self.assertEqual(body["registration_id"], reg.id)
        self.assertEqual(body["amount"], 1500)  # female price
        mock_retrieve.assert_called_once_with("pi_abc")

    def test_not_pending_returns_409(self):
        event = make_event()
        attendee = make_attendee(n=101)
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.get(f"/api/registrations/{reg.id}/payment/")
        self.assertEqual(resp.status_code, 409)

    def test_not_found(self):
        resp = self.client.get("/api/registrations/99999/payment/")
        self.assertEqual(resp.status_code, 404)

    def test_pending_no_intent_returns_409(self):
        event = make_event()
        attendee = make_attendee(n=102)
        reg = make_registration(
            event=event, attendee=attendee,
            status="pending", payment_intent_id="",
        )
        resp = self.client.get(f"/api/registrations/{reg.id}/payment/")
        self.assertEqual(resp.status_code, 409)
        self.assertIn("No payment intent", resp.json()["detail"])


# ============================================================================
# 11. POST /api/subscribe/
# ============================================================================


class SubscribeTest(TestCase):
    @patch(MAILERLITE_ADD)
    def test_subscribe(self, mock_add):
        resp = self.client.post(
            "/api/subscribe/",
            data=json.dumps({"email": "subscriber@example.com"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["detail"], "Subscribed")
        mock_add.assert_called_once_with("subscriber@example.com", "", "")


# ============================================================================
# 12. Auth endpoints
# ============================================================================


class AuthLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "testadmin", password="testpass", is_staff=True
        )

    def test_login_success(self):
        resp = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": "testadmin", "password": "testpass"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["detail"], "Logged in")

    def test_login_fail(self):
        resp = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": "testadmin", "password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)


class AuthLogoutTest(TestCase):
    def test_logout(self):
        user = User.objects.create_user("logoutuser", password="pass", is_staff=True)
        self.client.force_login(user)
        resp = self.client.post("/api/auth/logout/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["detail"], "Logged out")


class AuthMeTest(TestCase):
    def test_authenticated_staff(self):
        user = User.objects.create_user("staffuser", password="pass", is_staff=True)
        self.client.force_login(user)
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["username"], "staffuser")
        self.assertTrue(body["is_staff"])

    def test_unauthenticated(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 401)

    def test_non_staff_user(self):
        user = User.objects.create_user("regular", password="pass", is_staff=False)
        self.client.force_login(user)
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, 401)


# ============================================================================
# 13. GET /api/match-form/{token}/
# ============================================================================


class GetMatchFormTest(TestCase):
    def setUp(self):
        self.event = make_event(status="closed")
        self.female_attendee = make_attendee(n=200, gender="female")
        self.reg = make_registration(
            event=self.event, attendee=self.female_attendee, status="confirmed",
        )
        # Create opposite-gender registrations
        self.male_attendee = make_attendee(n=201, gender="male")
        self.male_reg = make_registration(
            event=self.event, attendee=self.male_attendee, status="confirmed",
        )

    def test_valid_token_closed_event(self):
        resp = self.client.get(f"/api/match-form/{self.reg.match_token}/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["event_title"], self.event.title)
        self.assertEqual(body["attendee_name"], self.female_attendee.first_name)
        self.assertFalse(body["already_submitted"])
        # Should see the male attendee
        self.assertEqual(len(body["attendees"]), 1)

    def test_draft_event_returns_404(self):
        event = make_event(status="draft")
        attendee = make_attendee(n=202, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.get(f"/api/match-form/{reg.match_token}/")
        self.assertEqual(resp.status_code, 404)

    def test_open_event_returns_404(self):
        event = make_event(status="open")
        attendee = make_attendee(n=203, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.get(f"/api/match-form/{reg.match_token}/")
        self.assertEqual(resp.status_code, 404)

    def test_completed_event_returns_410(self):
        event = make_event(status="completed")
        attendee = make_attendee(n=204, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.get(f"/api/match-form/{reg.match_token}/")
        self.assertEqual(resp.status_code, 410)

    def test_invalid_token_returns_404(self):
        resp = self.client.get("/api/match-form/00000000-0000-0000-0000-000000000000/")
        self.assertEqual(resp.status_code, 404)

    def test_already_submitted(self):
        make_submission(self.event, self.reg, selected_regs=[self.male_reg])
        resp = self.client.get(f"/api/match-form/{self.reg.match_token}/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body["already_submitted"])
        self.assertEqual(len(body["previous_selections"]), 1)


# ============================================================================
# 14. POST /api/match-form/{token}/
# ============================================================================


class SubmitMatchFormTest(TestCase):
    def setUp(self):
        self.event = make_event(status="closed")
        self.female_attendee = make_attendee(n=210, gender="female")
        self.reg = make_registration(
            event=self.event, attendee=self.female_attendee, status="confirmed",
        )
        self.male_attendee = make_attendee(n=211, gender="male")
        self.male_reg = make_registration(
            event=self.event, attendee=self.male_attendee, status="confirmed",
        )

    def test_successful_submission(self):
        resp = self.client.post(
            f"/api/match-form/{self.reg.match_token}/",
            data=json.dumps({"selected_ids": [self.male_reg.id]}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["detail"], "Submission recorded")
        self.assertTrue(MatchSubmission.objects.filter(submitted_by=self.reg).exists())

    def test_already_submitted_returns_409(self):
        make_submission(self.event, self.reg, selected_regs=[self.male_reg])
        resp = self.client.post(
            f"/api/match-form/{self.reg.match_token}/",
            data=json.dumps({"selected_ids": [self.male_reg.id]}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 409)
        self.assertIn("Already submitted", resp.json()["detail"])

    def test_completed_event_returns_410(self):
        event = make_event(status="completed")
        attendee = make_attendee(n=212, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.post(
            f"/api/match-form/{reg.match_token}/",
            data=json.dumps({"selected_ids": []}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 410)

    def test_invalid_token_returns_404(self):
        resp = self.client.post(
            "/api/match-form/00000000-0000-0000-0000-000000000000/",
            data=json.dumps({"selected_ids": []}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)

    def test_draft_event_returns_404(self):
        event = make_event(status="draft")
        attendee = make_attendee(n=213, gender="female")
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        resp = self.client.post(
            f"/api/match-form/{reg.match_token}/",
            data=json.dumps({"selected_ids": []}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)


# ============================================================================
# 15. Admin endpoints
# ============================================================================


class AdminBaseTest(TestCase):
    """Base class for admin endpoint tests that sets up staff auth."""

    def setUp(self):
        from django.contrib.auth.models import User

        self.staff_user = User.objects.create_user(
            "admin", password="pass", is_staff=True
        )
        self.client.force_login(self.staff_user)


class AdminListEventsTest(AdminBaseTest):
    def test_list_all_events(self):
        make_event(status="open")
        make_event(status="draft")
        make_event(status="closed")
        resp = self.client.get("/api/admin/events/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 3)

    def test_unauthenticated_returns_401(self):
        self.client.logout()
        resp = self.client.get("/api/admin/events/")
        self.assertEqual(resp.status_code, 401)


class AdminCreateEventTest(AdminBaseTest):
    def test_create_event(self):
        payload = {
            "event_date": "2026-06-15T18:00:00",
            "min_age": 25,
            "max_age": 45,
            "capacity": 32,
            "max_male_ratio": 0.55,
            "status": "draft",
        }
        resp = self.client.post(
            "/api/admin/events/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertEqual(body["capacity"], 32)
        self.assertEqual(Event.objects.count(), 1)


class AdminUpdateEventTest(AdminBaseTest):
    def test_update_event(self):
        event = make_event()
        payload = {
            "event_date": "2026-07-01T18:00:00",
            "min_age": 30,
            "max_age": 50,
            "capacity": 40,
            "max_male_ratio": 0.5,
            "status": "open",
        }
        resp = self.client.put(
            f"/api/admin/events/{event.id}/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.capacity, 40)

    def test_update_not_found(self):
        payload = {
            "event_date": "2026-07-01T18:00:00",
            "min_age": 30,
            "max_age": 50,
            "capacity": 40,
            "max_male_ratio": 0.5,
            "status": "open",
        }
        resp = self.client.put(
            "/api/admin/events/99999/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 404)


class AdminDeleteEventTest(AdminBaseTest):
    def test_delete_event(self):
        event = make_event()
        resp = self.client.delete(f"/api/admin/events/{event.id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Event.objects.filter(id=event.id).exists())

    def test_delete_not_found(self):
        resp = self.client.delete("/api/admin/events/99999/")
        self.assertEqual(resp.status_code, 404)


class AdminGetRegistrationsTest(AdminBaseTest):
    def test_get_registrations(self):
        event = make_event()
        attendee = make_attendee(n=300)
        make_registration(event=event, attendee=attendee)
        resp = self.client.get(f"/api/admin/events/{event.id}/registrations/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_event_not_found(self):
        resp = self.client.get("/api/admin/events/99999/registrations/")
        self.assertEqual(resp.status_code, 404)


class AdminGetStatsTest(AdminBaseTest):
    def test_get_stats(self):
        event = make_event()
        m = make_attendee(n=310, gender="male")
        f = make_attendee(n=311, gender="female")
        make_registration(event=event, attendee=m, status="confirmed")
        make_registration(event=event, attendee=f, status="confirmed")
        resp = self.client.get(f"/api/admin/events/{event.id}/stats/")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["confirmed"], 2)
        self.assertEqual(body["male_count"], 1)
        self.assertEqual(body["female_count"], 1)
        self.assertEqual(body["revenue"], 1500 + 2000)

    def test_event_not_found(self):
        resp = self.client.get("/api/admin/events/99999/stats/")
        self.assertEqual(resp.status_code, 404)


class AdminGetMatchesTest(AdminBaseTest):
    def test_get_matches(self):
        event = make_event()
        a = make_attendee(n=320, gender="male")
        b = make_attendee(n=321, gender="female")
        reg_a = make_registration(event=event, attendee=a)
        reg_b = make_registration(event=event, attendee=b)
        make_match(event, reg_a, reg_b)
        resp = self.client.get(f"/api/admin/events/{event.id}/matches/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_event_not_found(self):
        resp = self.client.get("/api/admin/events/99999/matches/")
        self.assertEqual(resp.status_code, 404)


class AdminGetMatchSubmissionsTest(AdminBaseTest):
    def test_get_match_submissions(self):
        event = make_event()
        a = make_attendee(n=330, gender="female")
        b = make_attendee(n=331, gender="male")
        reg_a = make_registration(event=event, attendee=a)
        reg_b = make_registration(event=event, attendee=b)
        make_submission(event, reg_a, selected_regs=[reg_b])
        resp = self.client.get(f"/api/admin/events/{event.id}/match-submissions/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(len(data[0]["selected_names"]), 1)

    def test_event_not_found(self):
        resp = self.client.get("/api/admin/events/99999/match-submissions/")
        self.assertEqual(resp.status_code, 404)


class AdminTriggerCommandTest(AdminBaseTest):
    @patch("django.core.management.call_command")
    def test_allowed_command(self, mock_call):
        event = make_event()
        resp = self.client.post(
            f"/api/admin/events/{event.id}/trigger/process_matches/"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("process_matches", resp.json()["detail"])
        mock_call.assert_called_once_with("process_matches")

    def test_disallowed_command(self):
        event = make_event()
        resp = self.client.post(
            f"/api/admin/events/{event.id}/trigger/drop_database/"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Unknown command", resp.json()["detail"])

    def test_event_not_found(self):
        resp = self.client.post("/api/admin/events/99999/trigger/process_matches/")
        self.assertEqual(resp.status_code, 404)
