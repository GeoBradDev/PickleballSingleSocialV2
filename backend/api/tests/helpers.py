"""Test factory helpers for creating model instances."""

from datetime import timedelta

from django.utils import timezone

from api.models import (
    Attendee,
    EmailLog,
    Event,
    Match,
    MatchSubmission,
    Registration,
)


def make_event(**kwargs):
    defaults = {
        "min_age": 25,
        "max_age": 45,
        "event_date": timezone.now() + timedelta(days=14),
        "capacity": 32,
        "max_male_ratio": 0.55,
        "status": "open",
    }
    defaults.update(kwargs)
    return Event.objects.create(**defaults)


def make_attendee(n=1, **kwargs):
    defaults = {
        "first_name": f"Test{n}",
        "last_name": f"User{n}",
        "email": f"test{n}@example.com",
        "phone": "5551234567",
        "gender": "female",
        "age": 30,
        "experience": "beginner",
    }
    defaults.update(kwargs)
    return Attendee.objects.create(**defaults)


def make_registration(event=None, attendee=None, **kwargs):
    if event is None:
        event = make_event()
    if attendee is None:
        attendee = make_attendee()
    defaults = {
        "event": event,
        "attendee": attendee,
        "status": "confirmed",
    }
    defaults.update(kwargs)
    return Registration.objects.create(**defaults)


def make_match(event, reg_a, reg_b, **kwargs):
    defaults = {
        "event": event,
        "attendee_a": reg_a,
        "attendee_b": reg_b,
    }
    defaults.update(kwargs)
    return Match.objects.create(**defaults)


def make_submission(event, registration, selected_regs=None):
    sub = MatchSubmission.objects.create(event=event, submitted_by=registration)
    if selected_regs:
        sub.selected_attendees.set(selected_regs)
    return sub
