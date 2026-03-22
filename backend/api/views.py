import json

import stripe
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ninja import NinjaAPI, Router

from .auth import staff_auth
from .models import Attendee, Event, Match, MatchSubmission, Registration
from .schemas import (
    ErrorOut,
    EventIn,
    EventOut,
    EventStatsOut,
    LoginIn,
    MatchFormAttendeeOut,
    MatchFormDataOut,
    MatchFormSubmissionIn,
    MatchOut,
    MatchSubmissionOut,
    PaymentIntentOut,
    RegistrationDetailOut,
    RegistrationIn,
    RegistrationOut,
    SubscribeIn,
    TriggerOut,
)

api = NinjaAPI(title="Pickleball Singles Social API", version="1.0.0")


def _annotate_events(qs):
    """Add male_count and female_count annotations to an Event queryset."""
    return qs.annotate(
        male_count=Count(
            "registrations",
            filter=Q(registrations__status="confirmed", registrations__attendee__gender="male"),
        ),
        female_count=Count(
            "registrations",
            filter=Q(registrations__status="confirmed", registrations__attendee__gender="female"),
        ),
    )


@api.get("/events/", response=list[EventOut])
def list_events(request: HttpRequest):
    events = _annotate_events(Event.objects.filter(status="open"))
    return events


@api.get("/events/{event_id}/", response={200: EventOut, 404: ErrorOut})
def get_event(request: HttpRequest, event_id: int):
    qs = _annotate_events(Event.objects.filter(id=event_id))
    event = qs.first()
    if not event:
        return 404, {"detail": "Event not found"}
    return 200, event


@api.post(
    "/events/{event_id}/register/",
    response={200: PaymentIntentOut, 400: ErrorOut, 404: ErrorOut},
)
def register_for_event(request: HttpRequest, event_id: int, payload: RegistrationIn):
    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return 404, {"detail": "Event not found"}

    # Check capacity
    confirmed_count = Registration.objects.filter(event=event, status="confirmed").count()
    if confirmed_count >= event.capacity:
        return 400, {"detail": "Event is full"}

    # Get or create attendee by email, updating other fields
    attendee, _ = Attendee.objects.update_or_create(
        email=payload.email,
        defaults={
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "phone": payload.phone,
            "gender": payload.gender,
            "age_group": payload.age_group,
            "contact_preference": payload.contact_preference,
        },
    )

    # Create registration
    registration, created = Registration.objects.get_or_create(
        event=event,
        attendee=attendee,
        defaults={"status": "pending"},
    )

    if not created and registration.status == "confirmed":
        return 400, {"detail": "Already registered and confirmed for this event"}

    # Create Stripe PaymentIntent
    stripe.api_key = settings.STRIPE_SECRET_KEY
    amount = 1500 if attendee.gender == "female" else 2000

    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="usd",
        metadata={
            "registration_id": str(registration.id),
            "event_id": str(event.id),
        },
    )

    registration.payment_intent_id = intent.id
    registration.save()

    return 200, {
        "client_secret": intent.client_secret,
        "registration_id": registration.id,
    }


@csrf_exempt
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    """Raw Django view for Stripe webhook (not Ninja) to preserve raw body for signature verification."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse("Invalid signature", status=400)

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        registration_id = payment_intent.get("metadata", {}).get("registration_id")
        if registration_id:
            Registration.objects.filter(id=registration_id).update(status="confirmed")
            try:
                from api.services.emails import send_registration_confirmation

                reg = Registration.objects.select_related("attendee", "event").get(
                    id=registration_id
                )
                send_registration_confirmation(reg)
            except Registration.DoesNotExist:
                pass

    return HttpResponse("OK", status=200)


@api.post("/subscribe/", auth=None)
def subscribe(request: HttpRequest, payload: SubscribeIn):
    from .services.mailerlite import add_subscriber

    add_subscriber(payload.email, "", "")
    return {"detail": "Subscribed"}


# ---------------------------------------------------------------------------
# Auth endpoints (public, no staff_auth required)
# ---------------------------------------------------------------------------

@api.post("/auth/login/", auth=None)
def auth_login(request: HttpRequest, payload: LoginIn):
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        return api.create_response(request, {"detail": "Invalid credentials"}, status=401)
    login(request, user)
    return {"detail": "Logged in"}


@api.post("/auth/logout/", auth=None)
def auth_logout(request: HttpRequest):
    logout(request)
    return {"detail": "Logged out"}


@api.get("/auth/me/", auth=None)
def auth_me(request: HttpRequest):
    if request.user.is_authenticated and request.user.is_staff:
        return {"username": request.user.username, "is_staff": True}
    return api.create_response(request, {"detail": "Not authenticated"}, status=401)


# ---------------------------------------------------------------------------
# Match form endpoints (public, token-based access)
# ---------------------------------------------------------------------------


@api.get("/match-form/{match_token}/", auth=None, response={200: MatchFormDataOut, 404: ErrorOut, 410: ErrorOut})
def get_match_form(request: HttpRequest, match_token: str):
    try:
        registration = Registration.objects.select_related("attendee", "event").get(
            match_token=match_token
        )
    except Registration.DoesNotExist:
        return 404, {"detail": "Not found"}

    event = registration.event
    if event.status in ("draft", "open"):
        return 404, {"detail": "Not found"}
    if event.status == "completed":
        return 410, {"detail": "Match form is closed"}

    # Get opposite-gender confirmed registrations
    viewer_gender = registration.attendee.gender
    opposite_regs = (
        Registration.objects.filter(event=event, status="confirmed")
        .exclude(attendee__gender=viewer_gender)
        .select_related("attendee")
        .order_by("attendee__first_name", "attendee__last_name")
    )

    attendees = [
        MatchFormAttendeeOut(
            registration_id=reg.id,
            display_name=f"{reg.attendee.first_name} {reg.attendee.last_name[0]}.",
        )
        for reg in opposite_regs
    ]

    # Check for existing submission
    already_submitted = False
    previous_selections = []
    submission = MatchSubmission.objects.filter(submitted_by=registration).first()
    if submission:
        already_submitted = True
        previous_selections = list(
            submission.selected_attendees.values_list("id", flat=True)
        )

    return 200, MatchFormDataOut(
        event_title=event.title,
        event_date=event.event_date.isoformat(),
        attendee_name=registration.attendee.first_name,
        attendees=attendees,
        already_submitted=already_submitted,
        previous_selections=previous_selections,
    )


@api.post("/match-form/{match_token}/", auth=None, response={200: ErrorOut, 404: ErrorOut, 409: ErrorOut, 410: ErrorOut})
def submit_match_form(request: HttpRequest, match_token: str, payload: MatchFormSubmissionIn):
    try:
        registration = Registration.objects.select_related("event").get(
            match_token=match_token
        )
    except Registration.DoesNotExist:
        return 404, {"detail": "Not found"}

    event = registration.event
    if event.status in ("draft", "open"):
        return 404, {"detail": "Not found"}
    if event.status == "completed":
        return 410, {"detail": "Match form is closed"}

    # Check if already submitted
    if MatchSubmission.objects.filter(submitted_by=registration).exists():
        return 409, {"detail": "Already submitted"}

    # Create submission
    submission = MatchSubmission.objects.create(
        event=event,
        submitted_by=registration,
    )
    submission.selected_attendees.set(payload.selected_ids)

    return 200, {"detail": "Submission recorded"}


# ---------------------------------------------------------------------------
# Admin router (staff-only)
# ---------------------------------------------------------------------------

admin_router = Router(auth=staff_auth, tags=["admin"])


@admin_router.get("/events/", response=list[EventOut])
def admin_list_events(request: HttpRequest):
    return _annotate_events(Event.objects.all().order_by("-event_date"))


@admin_router.post("/events/", response={201: EventOut})
def admin_create_event(request: HttpRequest, payload: EventIn):
    event = Event.objects.create(**payload.dict())
    qs = _annotate_events(Event.objects.filter(id=event.id))
    return 201, qs.first()


@admin_router.put("/events/{event_id}/", response={200: EventOut, 404: ErrorOut})
def admin_update_event(request: HttpRequest, event_id: int, payload: EventIn):
    updated = Event.objects.filter(id=event_id).update(**payload.dict())
    if not updated:
        return 404, {"detail": "Event not found"}
    qs = _annotate_events(Event.objects.filter(id=event_id))
    return 200, qs.first()


@admin_router.delete("/events/{event_id}/", response={204: None, 404: ErrorOut})
def admin_delete_event(request: HttpRequest, event_id: int):
    deleted, _ = Event.objects.filter(id=event_id).delete()
    if not deleted:
        return 404, {"detail": "Event not found"}
    return 204, None


@admin_router.get(
    "/events/{event_id}/registrations/",
    response={200: list[RegistrationDetailOut], 404: ErrorOut},
)
def admin_event_registrations(request: HttpRequest, event_id: int):
    if not Event.objects.filter(id=event_id).exists():
        return 404, {"detail": "Event not found"}
    registrations = (
        Registration.objects.filter(event_id=event_id)
        .select_related("attendee")
        .order_by("-created_at")
    )
    results = []
    for reg in registrations:
        results.append(
            {
                "id": reg.id,
                "status": reg.status,
                "match_token": str(reg.match_token),
                "created_at": reg.created_at.isoformat(),
                "attendee_first_name": reg.attendee.first_name,
                "attendee_last_name": reg.attendee.last_name,
                "attendee_email": reg.attendee.email,
                "attendee_phone": reg.attendee.phone,
                "attendee_gender": reg.attendee.gender,
                "attendee_contact_preference": reg.attendee.contact_preference,
            }
        )
    return 200, results


@admin_router.get(
    "/events/{event_id}/stats/",
    response={200: EventStatsOut, 404: ErrorOut},
)
def admin_event_stats(request: HttpRequest, event_id: int):
    if not Event.objects.filter(id=event_id).exists():
        return 404, {"detail": "Event not found"}
    regs = Registration.objects.filter(event_id=event_id).select_related("attendee")
    total = regs.count()
    confirmed = regs.filter(status="confirmed").count()
    pending = regs.filter(status="pending").count()
    confirmed_regs = regs.filter(status="confirmed")
    male_count = confirmed_regs.filter(attendee__gender="male").count()
    female_count = confirmed_regs.filter(attendee__gender="female").count()
    revenue = (female_count * 1500) + (male_count * 2000)
    return 200, {
        "total_registrations": total,
        "confirmed": confirmed,
        "pending": pending,
        "male_count": male_count,
        "female_count": female_count,
        "revenue": revenue,
    }


@admin_router.get(
    "/events/{event_id}/matches/",
    response={200: list[MatchOut], 404: ErrorOut},
)
def admin_event_matches(request: HttpRequest, event_id: int):
    if not Event.objects.filter(id=event_id).exists():
        return 404, {"detail": "Event not found"}
    matches = (
        Match.objects.filter(event_id=event_id)
        .select_related("attendee_a__attendee", "attendee_b__attendee")
        .order_by("-created_at")
    )
    results = []
    for m in matches:
        a = m.attendee_a.attendee
        b = m.attendee_b.attendee
        results.append(
            {
                "id": m.id,
                "attendee_a_name": f"{a.first_name} {a.last_name[0]}.",
                "attendee_b_name": f"{b.first_name} {b.last_name[0]}.",
                "notified": m.notified,
                "created_at": m.created_at.isoformat(),
            }
        )
    return 200, results


@admin_router.get(
    "/events/{event_id}/match-submissions/",
    response={200: list[MatchSubmissionOut], 404: ErrorOut},
)
def admin_event_match_submissions(request: HttpRequest, event_id: int):
    if not Event.objects.filter(id=event_id).exists():
        return 404, {"detail": "Event not found"}
    submissions = (
        MatchSubmission.objects.filter(event_id=event_id)
        .select_related("submitted_by__attendee")
        .prefetch_related("selected_attendees__attendee")
        .order_by("-submitted_at")
    )
    results = []
    for sub in submissions:
        submitter = sub.submitted_by.attendee
        selected = [
            f"{sel.attendee.first_name} {sel.attendee.last_name[0]}."
            for sel in sub.selected_attendees.all()
        ]
        results.append(
            {
                "id": sub.id,
                "submitted_by_name": f"{submitter.first_name} {submitter.last_name[0]}.",
                "submitted_by_gender": submitter.gender,
                "selected_names": selected,
                "submitted_at": sub.submitted_at.isoformat(),
            }
        )
    return 200, results


@admin_router.post(
    "/events/{event_id}/trigger/{command}/",
    response={200: TriggerOut, 400: ErrorOut, 404: ErrorOut},
)
def admin_trigger_command(request: HttpRequest, event_id: int, command: str):
    if not Event.objects.filter(id=event_id).exists():
        return 404, {"detail": "Event not found"}
    allowed_commands = ("process_matches", "send_match_emails")
    if command not in allowed_commands:
        return 400, {"detail": f"Unknown command. Allowed: {', '.join(allowed_commands)}"}
    from django.core.management import call_command
    call_command(command)
    return 200, {"detail": f"Successfully ran {command}"}


api.add_router("/admin/", admin_router)
