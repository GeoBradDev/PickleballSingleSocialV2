from ..models import EmailLog

# Marketing email schedule: (email_key, days_before_event)
MARKETING_SCHEDULE = [
    ("marketing_announcement", 28),
    ("marketing_registration_open", 21),
    ("marketing_spots_filling", 14),
    ("marketing_one_week", 7),
    ("marketing_last_chance", 3),
]

MARKETING_TEMPLATES = {
    "marketing_announcement": {
        "subject": "New Event: Pickleball Singles Social ({age_label}) - {date}",
        "html": """
        <h2>New Event Announced!</h2>
        <p>We're excited to announce our next Pickleball Singles Social
        for ages <strong>{age_label}</strong> on <strong>{date}</strong>!</p>
        <p>This is a fun, social event where you'll meet other singles
        who love pickleball. Space is limited to {capacity} players to keep
        things intimate and well-organized.</p>
        <p>Registration opens soon. Mark your calendar!</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           View Event Details</a></p>
        """,
    },
    "marketing_registration_open": {
        "subject": "Registration Open: {age_label} Singles Social on {date}",
        "html": """
        <h2>Registration Is Open!</h2>
        <p>Registration is now open for the <strong>{age_label}</strong>
        Pickleball Singles Social on <strong>{date}</strong>.</p>
        <p>We have {capacity} spots available and they tend to fill up
        quickly. Don't miss out!</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Register Now</a></p>
        """,
    },
    "marketing_spots_filling": {
        "subject": "Spots Filling Up: {age_label} Singles Social on {date}",
        "html": """
        <h2>Spots Are Filling Up!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social on
        <strong>{date}</strong> is filling up fast.</p>
        <p>If you've been thinking about joining, now is the time to
        secure your spot before we're full.</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Register Before It's Full</a></p>
        """,
        "full_subject": "Sold Out (Waitlist Open): {age_label} Singles Social on {date}",
        "full_html": """
        <h2>We're Sold Out!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social on
        <strong>{date}</strong> has filled all {capacity} spots.</p>
        <p>But don't worry, you can still join the waitlist. If a spot opens
        up, we'll let you know right away.</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Join the Waitlist</a></p>
        """,
    },
    "marketing_one_week": {
        "subject": "One Week Away: {age_label} Pickleball Singles Social",
        "html": """
        <h2>One Week Away!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        just one week away on <strong>{date}</strong>.</p>
        <p>There are still a few spots left. This is your chance to meet
        other pickleball-loving singles in a fun, organized setting.</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Grab Your Spot</a></p>
        """,
        "full_subject": "One Week Away (Waitlist Open): {age_label} Pickleball Singles Social",
        "full_html": """
        <h2>One Week Away!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        just one week away on <strong>{date}</strong>.</p>
        <p>All {capacity} spots are taken, but spots do open up. Join the
        waitlist and you'll be first in line if someone cancels.</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Join the Waitlist</a></p>
        """,
    },
    "marketing_last_chance": {
        "subject": "Last Chance: {age_label} Singles Social This {weekday}",
        "html": """
        <h2>Last Chance!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        this <strong>{weekday}</strong>, {date}.</p>
        <p>This is your last chance to register. Once spots are gone,
        they're gone!</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Register Now</a></p>
        """,
        "full_subject": "Waitlist Open: {age_label} Singles Social This {weekday}",
        "full_html": """
        <h2>Waitlist Still Open!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        this <strong>{weekday}</strong>, {date}.</p>
        <p>We're fully booked, but cancellations happen. Join the waitlist
        for a chance to get in.</p>
        <p><a href="{register_url}"
           style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
           Join the Waitlist</a></p>
        """,
    },
}


def render_marketing_email(email_key, event, full=False):
    """Render a marketing email template with event data. Returns (subject, html).

    If full=True and the template has full_subject/full_html variants,
    those are used instead (waitlist messaging).
    """
    template = MARKETING_TEMPLATES[email_key]
    context = {
        "age_label": event.age_label,
        "date": event.event_date.strftime("%B %-d, %Y"),
        "weekday": event.event_date.strftime("%A"),
        "capacity": str(event.capacity),
        "register_url": f"https://pickleballsinglessocial.com/events/{event.id}",
    }
    if full and "full_subject" in template:
        subject = template["full_subject"].format(**context)
        html = template["full_html"].format(**context)
    else:
        subject = template["subject"].format(**context)
        html = template["html"].format(**context)
    return subject, html


def _already_sent(attendee, event, email_type):
    return EmailLog.objects.filter(
        attendee=attendee, event=event, email_type=email_type
    ).exists()


def _log_email(attendee, event, email_type):
    EmailLog.objects.create(attendee=attendee, event=event, email_type=email_type)


def send_registration_confirmation(registration):
    """Send after payment confirmed."""
    email_type = "registration_confirmation"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"You're registered for {registration.event.title}!"
    html = f"""
    <h2>Registration Confirmed</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>You are confirmed for <strong>{registration.event.title}</strong>
    on {registration.event.event_date.strftime('%B %d, %Y')}.</p>
    <p>We'll send you a reminder as the event approaches.</p>
    """
    from .mailerlite import send_email, add_subscriber

    send_email(registration.attendee.email, subject, html)
    add_subscriber(
        registration.attendee.email,
        registration.attendee.first_name,
        registration.attendee.last_name,
    )
    _log_email(registration.attendee, registration.event, email_type)


def send_waitlist_notification(registration):
    """Notify registrant they are on the waitlist."""
    email_type = "waitlist_notification"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"You're on the waitlist for {registration.event.title}"
    html = f"""
    <h2>You're on the Waitlist</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for signing up for <strong>{registration.event.title}</strong>!</p>
    <p>We keep the group intentionally small and balanced,
    and we've currently filled our spots. You're on the waitlist.
    If an opening comes up, you'll hear from us right away.</p>
    <p>Questions? Just reply to this email.</p>
    """
    from .mailerlite import send_email, add_subscriber

    send_email(registration.attendee.email, subject, html)
    add_subscriber(
        registration.attendee.email,
        registration.attendee.first_name,
        registration.attendee.last_name,
    )
    _log_email(registration.attendee, registration.event, email_type)


def send_waitlist_promotion(registration):
    """Notify a promoted registrant that a spot opened up and they can now pay."""
    email_type = "waitlist_promotion"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    pay_url = (
        f"https://pickleballsinglessocial.com/events/{event.id}"
        f"/pay?registration={registration.id}"
    )
    subject = f"A spot opened up for {event.title}!"
    html = f"""
    <h2>A Spot Opened Up!</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>Good news: a spot has opened up for
    <strong>{event.title}</strong> on
    {event.event_date.strftime('%B %d, %Y')}!</p>
    <p>Complete payment to lock in your spot:</p>
    <p><a href="{pay_url}"
       style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">
       Pay and confirm your spot</a></p>
    <p>This link is first come, first served. If payment isn't completed soon,
    your spot may be offered to the next person on the waitlist.</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_payment_expired(registration):
    """Notify registrant their payment window has expired."""
    email_type = "payment_expired"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Your payment link has expired for {registration.event.title}"
    html = f"""
    <h2>Payment Link Expired</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>Your payment link for <strong>{registration.event.title}</strong>
    has expired and your spot has been released.</p>
    <p>If you're still interested, just reply to this email
    and we'll do our best to get you back in.</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_reminder(registration):
    """3-day-before reminder."""
    email_type = "reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Reminder: {registration.event.title} is coming up!"
    html = f"""
    <h2>Event Reminder</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{registration.event.title}</strong> is just a few days away on
    {registration.event.event_date.strftime('%B %d, %Y')}.</p>
    <p>We look forward to seeing you there!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_payment_reminder(registration):
    """Nudge pending registrations to complete payment."""
    email_type = "payment_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Complete your registration for {registration.event.title}"
    html = f"""
    <h2>Complete Your Registration</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>We noticed you started registering for <strong>{registration.event.title}</strong>
    but haven't completed payment yet.</p>
    <p>Spots are limited, so don't wait too long!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_dayof_reminder(registration):
    """Day-of reminder."""
    email_type = "dayof_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Today's the day! {registration.event.title}"
    html = f"""
    <h2>See You Today!</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{registration.event.title}</strong> is happening today!</p>
    <p>Have a great time on the courts!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_match_form_link(registration):
    """Post-event match form link."""
    email_type = "match_form"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"https://pickleballsinglessocial.com/match/{registration.match_token}"
    subject = f"Who did you connect with at {registration.event.title}?"
    html = f"""
    <h2>Match Form</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for attending <strong>{registration.event.title}</strong>!</p>
    <p>Now it's time to let us know who you'd like to connect with.
    Click below to select the people you enjoyed meeting:</p>
    <p><a href="{match_url}" style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">Open Match Form</a></p>
    <p>The form closes at midnight tonight, so don't wait!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_match_form_reminder(registration):
    """Remind non-submitters to complete match form."""
    email_type = "match_form_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"https://pickleballsinglessocial.com/match/{registration.match_token}"
    subject = f"Last chance: Submit your matches for {registration.event.title}"
    html = f"""
    <h2>Don't Forget!</h2>
    <p>Hi {registration.attendee.first_name},</p>
    <p>The match form for <strong>{registration.event.title}</strong> closes at midnight.</p>
    <p><a href="{match_url}" style="display:inline-block;padding:12px 24px;background:#2e7d32;color:white;text-decoration:none;border-radius:4px;">Submit Your Matches</a></p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, html)
    _log_email(registration.attendee, registration.event, email_type)


def send_match_notification(match):
    """Notify both parties of a mutual match with contact info."""
    _send_match_to(match, match.attendee_a, match.attendee_b)
    _send_match_to(match, match.attendee_b, match.attendee_a)


def _send_match_to(match, registration, other_registration):
    """Send match email to one party."""
    email_type = f"match_notification_{other_registration.id}"
    attendee = registration.attendee
    other = other_registration.attendee
    if _already_sent(attendee, match.event, email_type):
        return

    subject = f"You have a match from {match.event.title}!"
    html = f"""
    <h2>It's a Match!</h2>
    <p>Hi {attendee.first_name},</p>
    <p>Great news! You and <strong>{other.first_name} {other.last_name[0]}.</strong>
    both selected each other at <strong>{match.event.title}</strong>.</p>
    <p>Here's how to reach them:</p>
    <p>Email: {other.email}</p>
    <p>Don't be shy, reach out and set up a game!</p>
    """
    from .mailerlite import send_email

    send_email(attendee.email, subject, html)
    _log_email(attendee, match.event, email_type)


def send_save_the_date(attendee, event):
    """Announce next event to past attendees."""
    email_type = "save_the_date"
    if _already_sent(attendee, event, email_type):
        return
    subject = f"Save the Date: {event.title}"
    html = f"""
    <h2>Save the Date!</h2>
    <p>Hi {attendee.first_name},</p>
    <p>We have another event coming up: <strong>{event.title}</strong>
    on {event.event_date.strftime('%B %d, %Y')}.</p>
    <p>Registration opens soon. Stay tuned!</p>
    """
    from .mailerlite import send_email

    send_email(attendee.email, subject, html)
    _log_email(attendee, event, email_type)
