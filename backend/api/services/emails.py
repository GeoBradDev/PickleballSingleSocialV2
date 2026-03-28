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
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>View Event Details</a></p>
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
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Register Now</a></p>
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
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Register Before It's Full</a></p>
        """,
        "full_subject": "Sold Out (Waitlist Open): {age_label} Singles Social on {date}",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">We're Sold Out!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social on
        <strong>{date}</strong> has filled all {capacity} spots.</p>
        <p>But don't worry, you can still join the waitlist. If a spot opens
        up, we'll let you know right away.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Join the Waitlist</a></p>
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
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Grab Your Spot</a></p>
        """,
        "full_subject": "One Week Away (Waitlist Open): {age_label} Pickleball Singles Social",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">One Week Away!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        just one week away on <strong>{date}</strong>.</p>
        <p>All {capacity} spots are taken, but spots do open up. Join the
        waitlist and you'll be first in line if someone cancels.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Join the Waitlist</a></p>
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
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Register Now</a></p>
        """,
        "full_subject": "Waitlist Open: {age_label} Singles Social This {weekday}",
        "full_html": """
        <h2 style="font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;">Waitlist Still Open!</h2>
        <p>The <strong>{age_label}</strong> Pickleball Singles Social is
        this <strong>{weekday}</strong>, {date}.</p>
        <p>We're fully booked, but cancellations happen. Join the waitlist
        for a chance to get in.</p>
        <p style="text-align:center;padding:8px 0;">
        <a href="{register_url}" style="""
        + '"'
        + _BTN
        + '"'
        + """>Join the Waitlist</a></p>
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
    return EmailLog.objects.filter(
        attendee=attendee, event=event, email_type=email_type, status_code__gte=200, status_code__lt=300
    ).exists()


def _status_code(response):
    return response.status_code if response is not None else None


def _log_email(attendee, event, email_type, status_code=None):
    EmailLog.objects.create(attendee=attendee, event=event, email_type=email_type, status_code=status_code)


def _heading(text):
    return f"<h2 style=\"font-family:'Playfair Display','Georgia',serif;color:#3d2c2c;margin:0 0 16px;font-size:24px;\">{text}</h2>"


def _button(url, label):
    return f'<p style="text-align:center;padding:8px 0;"><a href="{url}" style="{_BTN}">{label}</a></p>'


def _event_details_block(event, include_coaching=True):
    """Reusable event details card for emails."""
    date_str = event.event_date.strftime("%A, %B %-d, %Y")
    coaching_row = """
    <tr>
    <td style="padding:6px 0;color:#7a6565;width:40%;vertical-align:top;">Coaching (optional)</td>
    <td style="padding:6px 0;font-weight:500;">2:30 PM</td>
    </tr>""" if include_coaching else ""
    return f"""
    <table style="margin:16px 0;background-color:#f8e1e8;border-radius:12px;width:100%;">
    <tr><td style="padding:20px;">
    <p style="margin:0 0 12px;font-weight:600;font-size:17px;color:#3d2c2c;">{event.title}</p>
    <table style="width:100%;font-size:14px;">
    <tr>
    <td style="padding:6px 0;color:#7a6565;width:40%;vertical-align:top;">Date</td>
    <td style="padding:6px 0;font-weight:500;">{date_str}</td>
    </tr>{coaching_row}
    <tr>
    <td style="padding:6px 0;color:#7a6565;vertical-align:top;">Play</td>
    <td style="padding:6px 0;font-weight:500;">3:00 - 5:00 PM</td>
    </tr>
    <tr>
    <td style="padding:6px 0;color:#7a6565;vertical-align:top;">Happy Hour</td>
    <td style="padding:6px 0;font-weight:500;">After play (optional)</td>
    </tr>
    <tr>
    <td style="padding:6px 0;color:#7a6565;vertical-align:top;">Location</td>
    <td style="padding:6px 0;font-weight:500;">Arch Pickleball &amp; Badminton<br>
    <span style="font-weight:400;color:#7a6565;">11333 Blake Dr, Bridgeton, MO 63044</span></td>
    </tr>
    <tr>
    <td style="padding:6px 0;color:#7a6565;vertical-align:top;">What to Bring</td>
    <td style="padding:6px 0;font-weight:500;">Comfortable clothes &amp; sneakers<br>
    <span style="font-weight:400;color:#7a6565;">Paddles and balls are provided</span></td>
    </tr>
    </table>
    </td></tr>
    </table>"""


def send_registration_confirmation(registration):
    """Send after payment confirmed."""
    email_type = "registration_confirmation"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"You're registered for {event.title}!"
    body = f"""
    {_heading("You're In!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Great news, your registration for <strong>{event.title}</strong> is confirmed!
    We're looking forward to seeing you on the courts.</p>
    {_event_details_block(event)}
    <p><strong>A few things to know:</strong></p>
    <ul style="padding-left:20px;color:#3d2c2c;">
    <li style="margin-bottom:8px;">No pickleball experience needed. The optional coaching session at 2:30 PM
    will get you comfortable before play starts.</li>
    <li style="margin-bottom:8px;">You'll rotate through mixed doubles partners so you get to meet everyone.</li>
    <li style="margin-bottom:8px;">After the event, you'll receive a private match form to let us know who you'd
    like to connect with. If it's mutual, we'll share contact info the next morning.</li>
    <li style="margin-bottom:8px;">Full refund available up to 48 hours before the event.</li>
    </ul>
    <p>We'll send you a reminder as the event approaches. See you there!</p>
    """
    from .mailerlite import add_subscriber, send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    add_subscriber(
        registration.attendee.email,
        registration.attendee.first_name,
        registration.attendee.last_name,
    )
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_waitlist_notification(registration):
    """Notify registrant they are on the waitlist."""
    email_type = "waitlist_notification"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"You're on the waitlist for {event.title}"
    body = f"""
    {_heading("You're on the Waitlist")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for signing up for <strong>{event.title}</strong>
    on {event.event_date.strftime("%A, %B %-d, %Y")}!</p>
    <p>We keep the group intentionally small (max {event.capacity} people) and balanced,
    and we've currently filled our spots for your group. You're on the waitlist,
    and if an opening comes up, you'll hear from us right away with a payment link
    to lock in your spot.</p>
    <p>There's no need to do anything else. We'll reach out if a spot opens up.</p>
    <p style="color:#7a6565;font-size:14px;">Questions? Just reply to this email.</p>
    """
    from .mailerlite import add_subscriber, send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    add_subscriber(
        registration.attendee.email,
        registration.attendee.first_name,
        registration.attendee.last_name,
    )
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


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
    <strong>{event.title}</strong>!</p>
    {_event_details_block(event)}
    <p>Complete payment to lock in your spot:</p>
    {_button(pay_url, "Pay and Confirm Your Spot")}
    <p style="color:#7a6565;font-size:14px;">This link is first come, first served.
    If payment isn't completed soon, your spot may be offered to the next person on the waitlist.</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_payment_expired(registration):
    """Notify registrant their payment window has expired."""
    email_type = "payment_expired"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"Your payment link has expired for {event.title}"
    body = f"""
    {_heading("Payment Link Expired")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Your payment link for <strong>{event.title}</strong>
    on {event.event_date.strftime("%A, %B %-d, %Y")} has expired and your spot has been released.</p>
    <p>If you're still interested, just reply to this email
    and we'll do our best to get you back in.</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_reminder(registration):
    """3-day-before reminder."""
    email_type = "reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"Reminder: {event.title} is coming up!"
    body = f"""
    {_heading("Your Event Is Almost Here!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{event.title}</strong> is just a few days away! Here's everything you need to know:</p>
    {_event_details_block(event)}
    <p><strong>Quick reminders:</strong></p>
    <ul style="padding-left:20px;color:#3d2c2c;">
    <li style="margin-bottom:8px;">Wear comfortable athletic clothes and court shoes (sneakers are fine).</li>
    <li style="margin-bottom:8px;">Paddles and balls are provided, so just bring yourself.</li>
    <li style="margin-bottom:8px;">If you're new to pickleball, come at 2:30 for the optional coaching session.</li>
    <li style="margin-bottom:8px;">After the event, check your email for the match form to let us know who you connected with.</li>
    </ul>
    <p>We're looking forward to seeing you there!</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_payment_reminder(registration):
    """Nudge pending registrations to complete payment."""
    email_type = "payment_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"Complete your registration for {event.title}"
    body = f"""
    {_heading("Complete Your Registration")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>We noticed you started registering for <strong>{event.title}</strong>
    on {event.event_date.strftime("%A, %B %-d, %Y")} but haven't completed payment yet.</p>
    <p>Spots are limited to {event.capacity} attendees, and we want to make sure you don't miss out.
    If you're still interested, complete your payment to lock in your spot.</p>
    <p style="color:#7a6565;font-size:14px;">If you changed your mind, no worries at all.
    We hope to see you at a future event!</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_dayof_reminder(registration):
    """Day-of reminder."""
    email_type = "dayof_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    event = registration.event
    subject = f"Today's the day! {event.title}"
    body = f"""
    {_heading("See You Today!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p><strong>{event.title}</strong> is happening today! Here's your quick reference:</p>
    {_event_details_block(event)}
    <p><strong>Last-minute tips:</strong></p>
    <ul style="padding-left:20px;color:#3d2c2c;">
    <li style="margin-bottom:8px;">Arrive a few minutes early to check in and grab a paddle.</li>
    <li style="margin-bottom:8px;">Bring water. There may be water available, but it's good to have your own.</li>
    <li style="margin-bottom:8px;">Come ready to have fun. This is social first, competitive second.</li>
    </ul>
    <p>After the event, you'll receive a link to our match form where you can privately select
    the people you'd like to connect with. If it's mutual, we'll share contact info tomorrow morning.</p>
    <p>See you on the courts!</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_match_form_link(registration):
    """Post-event match form link."""
    email_type = "match_form"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"{settings.SITE_URL}/match/{registration.match_token}"
    event = registration.event
    subject = f"Who did you connect with at {event.title}?"
    body = f"""
    {_heading("Who Did You Connect With?")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>Thanks for attending <strong>{event.title}</strong>! We hope you had a great time.</p>
    <p>Now it's time to let us know who you'd like to connect with. Here's how it works:</p>
    <ul style="padding-left:20px;color:#3d2c2c;">
    <li style="margin-bottom:8px;">Click the button below to open your private match form.</li>
    <li style="margin-bottom:8px;">Select the people you enjoyed meeting and would like to connect with.</li>
    <li style="margin-bottom:8px;">If the feeling is mutual (they also select you), we'll share
    contact info with both of you tomorrow morning.</li>
    <li style="margin-bottom:8px;">Your selections are completely private. No one sees who you picked
    unless it's a mutual match.</li>
    </ul>
    {_button(match_url, "Open Match Form")}
    <p style="color:#7a6565;font-size:14px;">The form closes tomorrow evening, so don't wait too long!</p>
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_match_form_reminder(registration):
    """Remind non-submitters to complete match form."""
    email_type = "match_form_reminder"
    if _already_sent(registration.attendee, registration.event, email_type):
        return
    match_url = f"{settings.SITE_URL}/match/{registration.match_token}"
    event = registration.event
    subject = f"Last chance: Submit your matches for {event.title}"
    body = f"""
    {_heading("Don't Forget Your Match Form!")}
    <p>Hi {registration.attendee.first_name},</p>
    <p>The match form for <strong>{event.title}</strong> closes tonight.
    If you haven't submitted yet, now's the time!</p>
    <p>Remember: your selections are completely private, and contact info is only shared
    if both people select each other. There's no downside to submitting.</p>
    {_button(match_url, "Submit Your Matches")}
    """
    from .mailerlite import send_email

    resp = send_email(registration.attendee.email, subject, _wrap_email(body))
    _log_email(registration.attendee, registration.event, email_type, _status_code(resp))


def send_combined_match_notification(event, registration, matched_registrations):
    """Send a single email listing all mutual matches for one attendee."""
    email_type = "match_notification"
    attendee = registration.attendee
    if _already_sent(attendee, event, email_type):
        return

    count = len(matched_registrations)
    plural = "matches" if count > 1 else "match"
    subject = f"You have {count} {plural} from {event.title}!"

    match_cards = ""
    for other_reg in matched_registrations:
        other = other_reg.attendee
        match_cards += f"""
        <tr><td style="padding:16px 20px;border-bottom:1px solid #fdf8f6;">
        <p style="margin:0 0 4px;font-weight:600;font-size:17px;color:#3d2c2c;">{other.first_name} {other.last_name[0]}.</p>
        <p style="margin:0;color:#7a6565;">
        <a href="mailto:{other.email}" style="color:#b5627e;">{other.email}</a></p>
        </td></tr>"""

    body = f"""
    {_heading("It's a Match!")}
    <p>Hi {attendee.first_name},</p>
    <p>Great news! You had <strong>{count} mutual {plural}</strong>
    at <strong>{event.title}</strong>.</p>
    <p>Here {"are the people" if count > 1 else "is the person"} who also selected you:</p>
    <table style="margin:16px 0;background-color:#f8e1e8;border-radius:12px;width:100%;">
    {match_cards}
    </table>
    <p>We suggest keeping it simple: introduce yourself, mention the event,
    and maybe suggest grabbing a coffee or playing some more pickleball together.</p>
    <p>Thanks for being part of Pickleball Singles Social. We hope this is the start
    of something great!</p>
    """
    from .mailerlite import send_email

    resp = send_email(attendee.email, subject, _wrap_email(body))
    _log_email(attendee, event, email_type, _status_code(resp))


def send_save_the_date(attendee, event):
    """Announce next event to past attendees."""
    email_type = "save_the_date"
    if _already_sent(attendee, event, email_type):
        return
    subject = f"Save the Date: {event.title}"
    body = f"""
    {_heading("Save the Date!")}
    <p>Hi {attendee.first_name},</p>
    <p>We have another event coming up and wanted to make sure you're the first to know!</p>
    {_event_details_block(event)}
    <p>Registration opens soon. As a past attendee, you'll get first access when spots open up.</p>
    <p>We hope to see you again on the courts!</p>
    """
    from .mailerlite import send_email

    resp = send_email(attendee.email, subject, _wrap_email(body))
    _log_email(attendee, event, email_type, _status_code(resp))
