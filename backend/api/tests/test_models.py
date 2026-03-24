import uuid
from datetime import datetime

from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from api.models import (
    Attendee,
    EmailLog,
    Event,
    MarketingEmailLog,
    Match,
    MatchSubmission,
    Registration,
)
from api.tests.helpers import (
    make_attendee,
    make_event,
    make_match,
    make_registration,
    make_submission,
)

EVENT_DATE = timezone.make_aware(datetime(2026, 4, 12, 15, 0))


# ------------------------------------------------------------------
# Event
# ------------------------------------------------------------------
class EventModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        self.assertEqual(str(event), "Event (2026-04-12)")

    def test_title_with_max_age(self):
        event = make_event(min_age=25, max_age=45, event_date=EVENT_DATE)
        self.assertEqual(
            event.title,
            "Pickleball Singles Social (25-45) - 4/12/2026",
        )

    def test_title_without_max_age(self):
        event = make_event(min_age=25, max_age=None, event_date=EVENT_DATE)
        self.assertEqual(
            event.title,
            "Pickleball Singles Social (25+) - 4/12/2026",
        )

    def test_age_label_with_max_age(self):
        event = make_event(min_age=30, max_age=50)
        self.assertEqual(event.age_label, "30-50")

    def test_age_label_without_max_age(self):
        event = make_event(min_age=30, max_age=None)
        self.assertEqual(event.age_label, "30+")

    def test_status_choices(self):
        keys = [choice[0] for choice in Event.STATUS_CHOICES]
        self.assertEqual(keys, ["draft", "open", "closed", "completed"])

    def test_default_status_is_draft(self):
        event = Event(event_date=EVENT_DATE)
        self.assertEqual(event.status, "draft")


# ------------------------------------------------------------------
# Attendee
# ------------------------------------------------------------------
class AttendeeModelTests(TestCase):
    def test_str(self):
        attendee = make_attendee(
            first_name="Jane", last_name="Doe", email="jane@example.com"
        )
        self.assertEqual(str(attendee), "Jane Doe (jane@example.com)")

    def test_unique_email_constraint(self):
        make_attendee(email="dupe@example.com")
        with self.assertRaises(IntegrityError):
            make_attendee(n=2, email="dupe@example.com")


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------
class RegistrationModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        attendee = make_attendee()
        reg = make_registration(event=event, attendee=attendee, status="confirmed")
        self.assertEqual(
            str(reg),
            f"{attendee} - {event} (confirmed)",
        )

    def test_unique_together_event_attendee(self):
        event = make_event()
        attendee = make_attendee()
        make_registration(event=event, attendee=attendee)
        with self.assertRaises(IntegrityError):
            make_registration(event=event, attendee=attendee)

    def test_default_match_token_is_uuid(self):
        reg = make_registration()
        self.assertIsInstance(reg.match_token, uuid.UUID)

    def test_match_tokens_are_unique_across_registrations(self):
        event = make_event()
        a1 = make_attendee(n=1)
        a2 = make_attendee(n=2)
        r1 = make_registration(event=event, attendee=a1)
        r2 = make_registration(event=event, attendee=a2)
        self.assertNotEqual(r1.match_token, r2.match_token)


# ------------------------------------------------------------------
# MatchSubmission
# ------------------------------------------------------------------
class MatchSubmissionModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        reg = make_registration(event=event, attendee=make_attendee())
        sub = make_submission(event=event, registration=reg)
        self.assertEqual(str(sub), f"Submission by {reg} for {event}")

    def test_m2m_selected_attendees(self):
        event = make_event()
        submitter = make_registration(event=event, attendee=make_attendee(n=1))
        selected_a = make_registration(event=event, attendee=make_attendee(n=2))
        selected_b = make_registration(event=event, attendee=make_attendee(n=3))
        sub = make_submission(
            event=event,
            registration=submitter,
            selected_regs=[selected_a, selected_b],
        )
        self.assertEqual(sub.selected_attendees.count(), 2)
        self.assertIn(selected_a, sub.selected_attendees.all())
        self.assertIn(selected_b, sub.selected_attendees.all())

    def test_m2m_empty_by_default(self):
        event = make_event()
        reg = make_registration(event=event, attendee=make_attendee())
        sub = make_submission(event=event, registration=reg)
        self.assertEqual(sub.selected_attendees.count(), 0)


# ------------------------------------------------------------------
# Match
# ------------------------------------------------------------------
class MatchModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        reg_a = make_registration(event=event, attendee=make_attendee(n=1))
        reg_b = make_registration(event=event, attendee=make_attendee(n=2))
        match = make_match(event=event, reg_a=reg_a, reg_b=reg_b)
        self.assertEqual(str(match), f"Match: {reg_a} <-> {reg_b}")

    def test_verbose_name_plural(self):
        self.assertEqual(Match._meta.verbose_name_plural, "matches")


# ------------------------------------------------------------------
# EmailLog
# ------------------------------------------------------------------
class EmailLogModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        attendee = make_attendee()
        log = EmailLog.objects.create(
            attendee=attendee, event=event, email_type="confirmation"
        )
        self.assertEqual(
            str(log), f"confirmation to {attendee} for {event}"
        )

    def test_unique_together_attendee_event_email_type(self):
        event = make_event()
        attendee = make_attendee()
        EmailLog.objects.create(
            attendee=attendee, event=event, email_type="confirmation"
        )
        with self.assertRaises(IntegrityError):
            EmailLog.objects.create(
                attendee=attendee, event=event, email_type="confirmation"
            )


# ------------------------------------------------------------------
# MarketingEmailLog
# ------------------------------------------------------------------
class MarketingEmailLogModelTests(TestCase):
    def test_str(self):
        event = make_event(event_date=EVENT_DATE)
        log = MarketingEmailLog.objects.create(
            event=event, email_key="launch_blast", subscriber_count=150
        )
        self.assertEqual(str(log), f"launch_blast for {event}")

    def test_unique_together_event_email_key(self):
        event = make_event()
        MarketingEmailLog.objects.create(event=event, email_key="launch_blast")
        with self.assertRaises(IntegrityError):
            MarketingEmailLog.objects.create(event=event, email_key="launch_blast")
