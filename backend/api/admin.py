from django.contrib import admin

from .models import Attendee, EmailLog, Event, Match, MatchSubmission, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "age_group", "event_date", "capacity", "status", "created_at")
    list_filter = ("status", "age_group")


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "gender", "age_group")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "status", "payment_intent_id", "created_at")
    list_filter = ("status",)


@admin.register(MatchSubmission)
class MatchSubmissionAdmin(admin.ModelAdmin):
    list_display = ("event", "submitted_by", "submitted_at")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("event", "attendee_a", "attendee_b", "notified", "created_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "email_type", "sent_at")
