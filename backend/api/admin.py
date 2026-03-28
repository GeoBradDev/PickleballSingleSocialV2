from django.contrib import admin

from .models import Attendee, EmailLog, Event, MarketingEmailLog, Match, MatchSubmission, Registration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("__str__", "min_age", "max_age", "event_date", "capacity", "max_male_ratio", "status", "created_at")
    list_filter = ("status",)


@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "gender", "age", "experience")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "status", "attending_coaching", "attending_happy_hour", "created_at")
    list_filter = ("status",)


@admin.register(MatchSubmission)
class MatchSubmissionAdmin(admin.ModelAdmin):
    list_display = ("event", "submitted_by", "submitted_at")


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("event", "attendee_a", "attendee_b", "notified", "created_at")


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("attendee", "event", "email_type", "status_code", "sent_at")


@admin.register(MarketingEmailLog)
class MarketingEmailLogAdmin(admin.ModelAdmin):
    list_display = ("event", "email_key", "sent_at", "subscriber_count")
