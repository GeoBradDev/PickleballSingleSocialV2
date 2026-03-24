import json
import logging

import stripe
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
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
    RegisterResponseOut,
    RegistrationDetailOut,
    RegistrationIn,
    RegistrationOut,
    RegistrationPaymentOut,
    SubscribeIn,
    TriggerOut,
)

logger = logging.getLogger("api.views")

api = NinjaAPI(title="Pickleball Singles Social API", version="1.0.0")


def _annotate_events(qs):
    """Add male_count, female_count, and registration_count annotations to an Event queryset."""
    return qs.annotate(
        male_count=Count(
            "registrations",
            filter=Q(registrations__status="confirmed", registrations__attendee__gender="male"),
        ),
        female_count=Count(
            "registrations",
            filter=Q(registrations__status="confirmed", registrations__attendee__gender="female"),
        ),
        registration_count=Count(
            "registrations",
            filter=Q(registrations__status__in=("confirmed", "pending", "waitlisted")),
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


def _get_price_cents(gender):
    """Return price in cents based on gender."""
    return 1500 if gender == "female" else 2000


def _check_capacity(event, gender):
    """Check whether there is capacity for a given gender at an event.

    Counts both confirmed and pending registrations as "reserved" spots.
    Women are only limited by total capacity.
    Men are limited by total capacity AND the max_male_ratio.
    """
    reserved = Registration.objects.filter(
        event=event, status__in=("confirmed", "pending")
    )
    total_reserved = reserved.count()
    if total_reserved >= event.capacity:
        return False
    if gender == "male":
        male_reserved = reserved.filter(attendee__gender="male").count()
        # Would adding one more male exceed the ratio?
        if (male_reserved + 1) / (total_reserved + 1) > event.max_male_ratio:
            return False
    return True


@api.post(
    "/events/{event_id}/register/",
    response={200: RegisterResponseOut, 400: ErrorOut, 404: ErrorOut},
)
def register_for_event(request: HttpRequest, event_id: int, payload: RegistrationIn):
    # Strip phone to digits for consistent storage
    phone_digits = "".join(c for c in payload.phone if c.isdigit())

    try:
        event = Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return 404, {"detail": "Event not found"}

    # Age validation
    if payload.age < event.min_age or (event.max_age is not None and payload.age > event.max_age):
        if event.max_age is None:
            msg = f"This event is for ages {event.age_label}. You must be {event.min_age} or older to register."
        else:
            msg = f"This event is for ages {event.age_label}. You must be between {event.min_age} and {event.max_age} to register."
        return 400, {"detail": msg}

    # Get or create attendee by email, updating other fields
    attendee, _ = Attendee.objects.update_or_create(
        email=payload.email,
        defaults={
            "first_name": payload.first_name,
            "last_name": payload.last_name,
            "phone": phone_digits,
            "gender": payload.gender,
            "age": payload.age,
            "experience": payload.experience,
        },
    )

    # Add to MailerLite subscriber list (non-critical, don't block registration)
    try:
        from api.services.mailerlite import add_subscriber
        add_subscriber(attendee.email, attendee.first_name, attendee.last_name)
    except Exception:
        logger.exception("Failed to add subscriber to MailerLite: %s", attendee.email)

    with transaction.atomic():
        # Lock the event row to prevent concurrent over-allocation
        event = Event.objects.select_for_update().get(id=event_id)

        # Check for existing registration
        registration, created = Registration.objects.get_or_create(
            event=event,
            attendee=attendee,
            defaults={
                "status": "pending",
                "attending_coaching": payload.attending_coaching,
                "attending_happy_hour": payload.attending_happy_hour,
            },
        )

        if not created:
            if registration.status == "confirmed":
                return 400, {"detail": "Already registered and confirmed for this event"}
            if registration.status == "waitlisted":
                return 200, {"registration_id": registration.id, "status": "waitlisted"}
            if registration.status == "pending" and registration.payment_intent_id:
                # Return existing PaymentIntent so they can retry payment
                stripe.api_key = settings.STRIPE_SECRET_KEY
                intent = stripe.PaymentIntent.retrieve(registration.payment_intent_id)
                return 200, {
                    "registration_id": registration.id,
                    "status": "pending",
                    "client_secret": intent.client_secret,
                }

        # Check gender-based capacity
        if not _check_capacity(event, attendee.gender):
            registration.status = "waitlisted"
            registration.save()
            logger.info(
                "Registration %d waitlisted: %s for %s (gender=%s)",
                registration.id, attendee.email, event.title, attendee.gender,
            )
            from api.services.emails import send_waitlist_notification
            send_waitlist_notification(registration)
            return 200, {"registration_id": registration.id, "status": "waitlisted"}

        # Create Stripe PaymentIntent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = _get_price_cents(attendee.gender)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "registration_id": str(registration.id),
                "event_id": str(event.id),
            },
        )

        registration.payment_intent_id = intent.id
        registration.status = "pending"
        registration.save()
        logger.info(
            "Registration %d pending: %s for %s (pi=%s)",
            registration.id, attendee.email, event.title, intent.id,
        )

    # A new registration may shift the ratio enough to promote waitlisted users
    # of the opposite gender (outside transaction to avoid holding lock during Stripe call)
    opposite = "female" if attendee.gender == "male" else "male"
    _try_promote_waitlisted(event, opposite)

    return 200, {
        "registration_id": registration.id,
        "status": "pending",
        "client_secret": intent.client_secret,
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
        logger.warning("Stripe webhook: invalid payload")
        return HttpResponse("Invalid payload", status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature")
        return HttpResponse("Invalid signature", status=400)

    event_type = event["type"]
    logger.info("Stripe webhook received: type=%s", event_type)

    if event_type == "payment_intent.succeeded":
        _handle_payment_succeeded(event["data"]["object"])
    elif event_type == "payment_intent.canceled":
        _handle_payment_canceled(event["data"]["object"])

    return HttpResponse("OK", status=200)


def _handle_payment_succeeded(payment_intent):
    """Handle successful payment: confirm registration, send email, check capacity."""
    registration_id = payment_intent.get("metadata", {}).get("registration_id")
    if not registration_id:
        logger.warning("payment_intent.succeeded missing registration_id in metadata")
        return

    try:
        reg = Registration.objects.select_related("attendee", "event").get(
            id=registration_id
        )
    except Registration.DoesNotExist:
        logger.error(
            "Registration %s not found for payment_intent.succeeded", registration_id
        )
        return

    # Idempotency: skip if already confirmed
    if reg.status == "confirmed":
        logger.info("Registration %d already confirmed, skipping", reg.id)
        return

    reg.status = "confirmed"
    reg.save()
    logger.info(
        "Registration %d confirmed: %s for %s",
        reg.id, reg.attendee.email, reg.event.title,
    )

    # Send confirmation email and add to MailerLite
    from api.services.emails import send_registration_confirmation
    send_registration_confirmation(reg)

    # Capacity warning
    confirmed_count = Registration.objects.filter(
        event=reg.event, status="confirmed"
    ).count()
    if confirmed_count > reg.event.capacity:
        logger.critical(
            "OVER CAPACITY: event=%d has %d confirmed (cap=%d)",
            reg.event.id, confirmed_count, reg.event.capacity,
        )


def _handle_payment_canceled(payment_intent):
    """Handle canceled/expired payment: mark expired, promote waitlisted."""
    registration_id = payment_intent.get("metadata", {}).get("registration_id")
    if not registration_id:
        return

    try:
        reg = Registration.objects.select_related("attendee", "event").get(
            id=registration_id
        )
    except Registration.DoesNotExist:
        return

    if reg.status != "pending":
        logger.info(
            "payment_intent.canceled for registration %d but status is %s, skipping",
            reg.id, reg.status,
        )
        return

    reg.status = "expired"
    reg.save()
    logger.info(
        "Registration %d expired: %s for %s",
        reg.id, reg.attendee.email, reg.event.title,
    )

    from api.services.emails import send_payment_expired
    send_payment_expired(reg)

    # Promote the next waitlisted person of the same gender
    _try_promote_waitlisted(reg.event, reg.attendee.gender)


def _try_promote_waitlisted(event, gender):
    """Promote the longest-waiting waitlisted registration for the given event and gender."""
    with transaction.atomic():
        event = Event.objects.select_for_update().get(id=event.id)

        waitlisted = (
            Registration.objects.filter(
                event=event, status="waitlisted", attendee__gender=gender
            )
            .select_related("attendee")
            .order_by("created_at")
            .first()
        )
        if not waitlisted:
            return

        # Verify capacity is still available
        if not _check_capacity(event, gender):
            return

        # Create PaymentIntent for promoted person
        stripe.api_key = settings.STRIPE_SECRET_KEY
        amount = _get_price_cents(gender)
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="usd",
            metadata={
                "registration_id": str(waitlisted.id),
                "event_id": str(event.id),
            },
        )

        waitlisted.status = "pending"
        waitlisted.payment_intent_id = intent.id
        waitlisted.save()
        logger.info(
            "Auto-promoted registration %d: %s (pi=%s)",
            waitlisted.id, waitlisted.attendee.email, intent.id,
        )

    from api.services.emails import send_waitlist_promotion
    send_waitlist_promotion(waitlisted)


@api.get(
    "/registrations/{registration_id}/payment/",
    auth=None,
    response={200: RegistrationPaymentOut, 404: ErrorOut, 409: ErrorOut},
)
def get_registration_payment(request: HttpRequest, registration_id: int):
    """Retrieve the PaymentIntent client_secret for a pending registration.

    Used by the frontend when a promoted-from-waitlist user follows their email link.
    """
    try:
        reg = Registration.objects.select_related("attendee").get(id=registration_id)
    except Registration.DoesNotExist:
        return 404, {"detail": "Registration not found"}

    if reg.status != "pending":
        return 409, {"detail": f"Registration is {reg.status}, not pending"}

    if not reg.payment_intent_id:
        return 409, {"detail": "No payment intent for this registration"}

    stripe.api_key = settings.STRIPE_SECRET_KEY
    intent = stripe.PaymentIntent.retrieve(reg.payment_intent_id)
    amount = _get_price_cents(reg.attendee.gender)

    return 200, {
        "client_secret": intent.client_secret,
        "registration_id": reg.id,
        "amount": amount,
    }


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
        event_date=event.event_date,
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
    event = Event.objects.create(**payload.model_dump())
    qs = _annotate_events(Event.objects.filter(id=event.id))
    return 201, qs.first()


@admin_router.put("/events/{event_id}/", response={200: EventOut, 404: ErrorOut})
def admin_update_event(request: HttpRequest, event_id: int, payload: EventIn):
    updated = Event.objects.filter(id=event_id).update(**payload.model_dump())
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
                "attendee_age": reg.attendee.age,
                "attendee_experience": reg.attendee.experience,
                "attending_coaching": reg.attending_coaching,
                "attending_happy_hour": reg.attending_happy_hour,
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
    waitlisted = regs.filter(status="waitlisted").count()
    confirmed_regs = regs.filter(status="confirmed")
    male_count = confirmed_regs.filter(attendee__gender="male").count()
    female_count = confirmed_regs.filter(attendee__gender="female").count()
    revenue = (female_count * 1500) + (male_count * 2000)
    return 200, {
        "total_registrations": total,
        "confirmed": confirmed,
        "pending": pending,
        "waitlisted": waitlisted,
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
