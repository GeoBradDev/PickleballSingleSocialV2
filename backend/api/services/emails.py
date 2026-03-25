from django.conf import settings

from ..models import EmailLog

# Marketing email schedule: (email_key, days_before_event)
MARKETING_SCHEDULE = [
    ("marketing_announcement", 28),
    ("marketing_registration_open", 21),
    ("marketing_spots_filling", 14),
    ("marketing_one_week", 7),
    ("marketing_last_chance", 3),
]


def _wrap_email(body_html):
    """Wrap email body content in the branded base template."""
    site_url = settings.SITE_URL
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pickleball Singles Social</title>
</head>
<body style="margin:0;padding:0;background-color:#fdf8f6;font-family:'Inter','Helvetica','Arial',sans-serif;color:#3d2c2c;line-height:1.7;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#fdf8f6;">
<tr><td align="center" style="padding:24px 16px;">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,#f8e1e8 0%,#fdf8f6 50%,#f5e6d0 100%);padding:32px 40px;text-align:center;">
<a href="{site_url}" style="text-decoration:none;">
<span style="font-family:'Playfair Display','Georgia',serif;font-size:24px;font-weight:700;color:#3d2c2c;letter-spacing:0.5px;">Pickleball Singles Social</span>
</a>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:32px 40px;font-size:16px;color:#3d2c2c;line-height:1.7;">
{body_html}
</td>
</tr>

<!-- Divider -->
<tr>
<td style="padding:0 40px;">
<hr style="border:none;border-top:1px solid #f8e1e8;margin:0;">
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:24px 40px;text-align:center;">
<p style="margin:0 0 8px;font-size:13px;color:#7a6565;">
<a href="{site_url}/events" style="color:#b5627e;text-decoration:none;">Events</a>
&nbsp;&middot;&nbsp;
<a href="{site_url}/about" style="color:#b5627e;text-decoration:none;">About</a>
&nbsp;&middot;&nbsp;
<a href="{site_url}/faq" style="color:#b5627e;text-decoration:none;">FAQ</a>
&nbsp;&middot;&nbsp;
<a href="{site_url}/code-of-conduct" style="color:#b5627e;text-decoration:none;">Code of Conduct</a>
</p>
<p style="margin:0 0 4px;font-size:12px;color:#7a6565;">
Hosted in partnership with Arch Pickleball &amp; Badminton, Bridgeton, MO
</p>
<p style="margin:0;font-size:12px;color:#7a6565;">
Pickleball Singles Social &middot; St. Louis, MO
</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>"""


# Shared button style
_BTN = (
    "display:inline-block;padding:14px 32px;background-color:#b5627e;"
    "color:#ffffff;text-decoration:none;border-radius:28px;font-weight:500;"
    "font-size:16px;font-family:'Inter','Helvetica','Arial',sans-serif;"
)


MARKETING_TEMPLATES = {
    "marketing_announcement": {
        "subject": "New Event: Pickleball Singles Social ({age_label}) - {date}",
        "html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">New Event Announced!</h2>
        <p>We're excited to announce our next Pickleball Singles Social
        for ages <strong>{age_label}</strong> on <strong>{date}</strong>!</p>
        <p>This is a fun, social event where you'll meet other singles
        who love pickleball. Space is limited to {capacity} players to keep
        things intimate and well-organized.</p>
        <p>Registration opens soon. Mark your calendar!</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>View Event Details</a></p>
        """,
    },
    "marketing_registration_open": {
        "subject": "Registration Open: {age_label} Singles Social on {date}",
        "html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">Registration Is Open!</h2>
        <p>Registration is now open for the <strong>{age_label}</strong>
        Pickleball Singles Social on <strong>{date}</strong>.</p>
        <p>We have {capacity} spots available and they tend to fill up
        quickly. Don't miss out!</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Register Now</a></p>
        """,
    },
    "marketing_spots_filling": {
        "subject": "Spots Filling Up: {age_label} Singles Social on {date}",
        "html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">Spots Are Filling Up!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social on
        <strong>{date}</strong> is filling up fast.</p>
        <p>If you've been thinking about joining, now is the time to
        secure your spot before we're full.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Register Before It's Full</a></p>
        """,
        "full_subject": "Sold Out (Waitlist Open): {age_label} Singles Social on {date}",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">We're Sold Out!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social on
        <strong>{date}</strong> has filled all {capacity} spots.</p>
        <p>But don't worry, you can still join the waitlist. If a spot opens
        up, we'll let you know right away.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Join the Waitlist</a></p>
        """,
    },
    "marketing_one_week": {
        "subject": "One Week Away: {age_label} Pickleball Singles Social",
        "html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">One Week Away!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        just one week away on <strong>{date}</strong>.</p>
        <p>There are still a few spots left. This is your chance to meet
        other pickleball-loving singles in a fun, organized setting.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Grab Your Spot</a></p>
        """,
        "full_subject": "One Week Away (Waitlist Open): {age_label} Pickleball Singles Social",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">One Week Away!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        just one week away on <strong>{date}</strong>.</p>
        <p>All {capacity} spots are taken, but spots do open up. Join the
        waitlist and you'll be first in line if someone cancels.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Join the Waitlist</a></p>
        """,
    },
    "marketing_last_chance": {
        "subject": "Last Chance: {age_label} Singles Social This {weekday}",
        "html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">Last Chance!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        this <strong>{weekday}</strong>, {date}.</p>
        <p>This is your last chance to register. Once spots are gone,
        they're gone!</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Register Now</a></p>
        """,
        "full_subject": "Waitlist Open: {age_label} Singles Social This {weekday}",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">Waitlist Still Open!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        this <strong>{weekday}</strong>, {date}.</p>
        <p>We're fully booked, but cancellations happen. Join the waitlist
        for a chance to get in.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style=""" + '"' + _BTN + '"' + """>Join the Waitlist</a></p>
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
        "register_url": f"{settings.SITE_URL}/events/{event.id}",
    }
    if full and "full_subject" in template:
        subject = template["full_subject"].format(**context)
        body = template["full_html"].format(**context)
    else:
        subject = template["subject"].format(**context)
        body = template["html"].format(**context)
    return subject, _wrap_email(body)


def _already_sent(attendee, event, email_type):
    return EmailLog.objects.filter(attendee=attendee, event=event, email_type=email_type).exists()


def _log_email(attendee, event, email_type):
    EmailLog.objects.create(attendee=attendee, event=event, email_type=email_type)


def _heading(text):
    return f'<h2 style="font-family:\'Playfair Display\',\'Georgia\',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">{text}</h2>'


def _button(url, label):
    return f'<p style="text-align:center;padding:8px 0;"><a href="{url}" style="{_BTN}">{label}</a></p>'


def send_registration_confirmation(registration):
    """Send after payment confirmed."""
    email_type = "registration_confirmation"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"You're registered for {registration.event.title}!"
    body = f"""
    {_heading("Registration Confirmed")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>You are confirmed for <strong>{registration.event.title}</strong>
    on {registration.event.event_date.strftime("%B %d, %Y")}.</p>
    <p>We'll send you a reminder as the event approaches.</p>
    """
    from .mailerlite import add_subscriber, send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
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
    body = f"""
    {_heading("You're on the Waitlist")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for signing up for <strong>{registration.event.title}</strong>!</p>
    <p>We keep the group intentionally small and balanced,
    and we've currently filled our spots. You're on the waitlist.
    If an opening comes up, you'll hear from us right away.</p>
    <p style="color:#7a6565;font-size:14px;">Questions? Just reply to this email.</p>
    """
    from .mailerlite import add_subscriber, send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
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
    pay_url = f"{settings.SITE_URL}/events/{event.id}/pay?token={registration.match_token}"
    subject = f"A spot opened up for {event.title}!"
    body = f"""
    {_heading("A Spot Opened Up!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Good news: a spot has opened up for
    <strong>{event.title}</strong> on
    {event.event_date.strftime("%B %d, %Y")}!</p>
    <p>Complete payment to lock in your spot:</p>
    {_button(pay_url, "Pay and Confirm Your Spot")}
    <p style="color:#7a6565;font-size:14px;">This link is first come, first served.
    If payment isn't completed soon, your spot may be offered to the next person on the waitlist.</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_payment_expired(registration):
    """Notify registrant their payment window has expired."""
    email_type = "payment_expired"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Your payment link has expired for {registration.event.title}"
    body = f"""
    {_heading("Payment Link Expired")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Your payment link for <strong>{registration.event.title}</strong>
    has expired and your spot has been released.</p>
    <p style="color:#7a6565;font-size:14px;">If you're still interested, just reply to this email
    and we'll do our best to get you back in.</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_reminder(registration):
    """3-day-before reminder."""
    email_type = "reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Reminder: {registration.event.title} is coming up!"
    body = f"""
    {_heading("Event Reminder")}
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{registration.event.title}</strong> is just a few days away on
    {registration.event.event_date.strftime("%B %d, %Y")}.</p>
    <p>We look forward to seeing you there!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_payment_reminder(registration):
    """Nudge pending registrations to complete payment."""
    email_type = "payment_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Complete your registration for {registration.event.title}"
    body = f"""
    {_heading("Complete Your Registration")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>We noticed you started registering for <strong>{registration.event.title}</strong>
    but haven't completed payment yet.</p>
    <p>Spots are limited, so don't wait too long!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_dayof_reminder(registration):
    """Day-of reminder."""
    email_type = "dayof_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    subject = f"Today's the day! {registration.event.title}"
    body = f"""
    {_heading("See You Today!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{registration.event.title}</strong> is happening today!</p>
    <p>Have a great time on the courts!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_match_form_link(registration):
    """Post-event match form link."""
    email_type = "match_form"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"{settings.SITE_URL}/match/{registration.match_token}"
    subject = f"Who did you connect with at {registration.event.title}?"
    body = f"""
    {_heading("Match Form")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for attending <strong>{registration.event.title}</strong>!</p>
    <p>Now it's time to let us know who you'd like to connect with.
    Click below to select the people you enjoyed meeting:</p>
    {_button(match_url, "Open Match Form")}
    <p style="color:#7a6565;font-size:14px;">The form closes at midnight tonight, so don't wait!</p>
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type)


def send_match_form_reminder(registration):
    """Remind non-submitters to complete match form."""
    email_type = "match_form_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"{settings.SITE_URL}/match/{registration.match_token}"
    subject = f"Last chance: Submit your matches for {registration.event.title}"
    body = f"""
    {_heading("Don't Forget!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>The match form for <strong>{registration.event.title}</strong> closes at midnight.</p>
    {_button(match_url, "Submit Your Matches")}
    """
    from .mailerlite import send_email

    send_email(registration.attendee.email, subject, _wrap_email(body))
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
    body = f"""
    {_heading("It's a Match!")}
    <p>Hi {attendee.first_name},</p>
    <p>Great news! You and <strong>{other.first_name} {other.last_name[0]}.</strong>
    both selected each other at <strong>{match.event.title}</strong>.</p>
    <p>Here's how to reach them:</p>
    <table style="margin:16px 0;background-color:#f8e1e8;border-radius:12px;padding:16px;width:100%;">
    <tr><td style="padding:16px;">
    <p style="margin:0 0 4px;font-weight:600;color:#3d2c2c;">{other.first_name} {other.last_name[0]}.</p>
    <p style="margin:0;color:#7a6565;"><a href="mailto:{other.email}" style="color:#b5627e;">{other.email}</a></p>
    </td></tr>
    </table>
    <p>Don't be shy, reach out and set up a game!</p>
    """
    from .mailerlite import send_email

    send_email(attendee.email, subject, _wrap_email(body))
    _log_email(attendee, match.event, email_type)


def send_save_the_date(attendee, event):
    """Announce next event to past attendees."""
    email_type = "save_the_date"
    if _already_sent(attendee, event, email_type):
        return
    subject = f"Save the Date: {event.title}"
    body = f"""
    {_heading("Save the Date!")}
    <p>Hi {attendee.first_name},</p>
    <p>We have another event coming up: <strong>{event.title}</strong>
    on {event.event_date.strftime("%B %d, %Y")}.</p>
    <p>Registration opens soon. Stay tuned!</p>
    """
    from .mailerlite import send_email

    send_email(attendee.email, subject, _wrap_email(body))
    _log_email(attendee, event, email_type)
