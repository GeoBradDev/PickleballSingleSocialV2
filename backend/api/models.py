import uuid

from django.db import models


class Event(models.Model):
    AGE_GROUP_CHOICES = [
        ("25-45", "25-45"),
        ("45+", "45+"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("closed", "Closed"),
        ("completed", "Completed"),
    ]

    title = models.CharField(max_length=255)
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES)
    event_date = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=32)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.event_date:%Y-%m-%d})"


class Attendee(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]
    AGE_GROUP_CHOICES = [
        ("25-45", "25-45"),
        ("45+", "45+"),
    ]
    CONTACT_PREFERENCE_CHOICES = [
        ("email", "Email"),
        ("text", "Text"),
        ("both", "Both"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES)
    contact_preference = models.CharField(
        max_length=10, choices=CONTACT_PREFERENCE_CHOICES, default="email"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Registration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    match_token = models.UUIDField(unique=True, default=uuid.uuid4)
    payment_intent_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("event", "attendee")]

    def __str__(self):
        return f"{self.attendee} - {self.event} ({self.status})"


class MatchSubmission(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    submitted_by = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="match_submissions"
    )
    selected_attendees = models.ManyToManyField(
        Registration, related_name="selected_by"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.submitted_by} for {self.event}"


class Match(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="matches")
    attendee_a = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="matches_as_a"
    )
    attendee_b = models.ForeignKey(
        Registration, on_delete=models.CASCADE, related_name="matches_as_b"
    )
    notified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.attendee_a} <-> {self.attendee_b}"

    class Meta:
        verbose_name_plural = "matches"


class EmailLog(models.Model):
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    email_type = models.CharField(max_length=50)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("attendee", "event", "email_type")]

    def __str__(self):
        return f"{self.email_type} to {self.attendee} for {self.event}"
