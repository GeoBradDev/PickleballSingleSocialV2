import uuid

from django.db import models


class Event(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("closed", "Closed"),
        ("completed", "Completed"),
    ]

    min_age = models.PositiveIntegerField(default=25)
    max_age = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for no upper limit.")
    event_date = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=32)
    max_male_ratio = models.FloatField(
        default=0.55,
        help_text="Maximum fraction of reserved spots that can be male (e.g. 0.5 = 50%).",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def title(self):
        return f"Pickleball Singles Social ({self.age_label}) - {self.event_date.strftime('%-m/%-d/%Y')}"

    @property
    def age_label(self):
        if self.max_age is None:
            return f"{self.min_age}+"
        return f"{self.min_age}-{self.max_age}"

    def __str__(self):
        return f"Event ({self.event_date:%Y-%m-%d})"


class Attendee(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
    ]

    EXPERIENCE_CHOICES = [
        ("none", "Never played"),
        ("beginner", "Beginner (played a few times)"),
        ("intermediate", "Intermediate (play regularly)"),
        ("advanced", "Advanced (competitive)"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    experience = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default="none")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class Registration(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("waitlisted", "Waitlisted"),
        ("confirmed", "Confirmed"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    attendee = models.ForeignKey(Attendee, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    attending_coaching = models.BooleanField(default=False)
    attending_happy_hour = models.BooleanField(default=False)
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
