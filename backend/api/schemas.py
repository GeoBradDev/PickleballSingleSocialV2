from datetime import datetime

from ninja import Schema


class EventOut(Schema):
    id: int
    title: str
    age_label: str
    min_age: int
    max_age: int | None
    event_date: datetime
    capacity: int
    status: str
    male_count: int = 0
    female_count: int = 0


class RegistrationIn(Schema):
    first_name: str
    last_name: str
    email: str
    phone: str
    gender: str
    age: int
    experience: str = "none"
    attending_coaching: bool = False
    attending_happy_hour: bool = False


class RegistrationOut(Schema):
    id: int
    status: str
    match_token: str


class PaymentIntentOut(Schema):
    client_secret: str
    registration_id: int


class RegisterResponseOut(Schema):
    registration_id: int
    status: str  # "pending" or "waitlisted"
    client_secret: str | None = None


class RegistrationPaymentOut(Schema):
    client_secret: str
    registration_id: int
    amount: int


class ErrorOut(Schema):
    detail: str


class EventIn(Schema):
    min_age: int = 25
    max_age: int | None = 45
    event_date: str
    capacity: int = 32
    max_male_ratio: float = 0.5
    status: str = "draft"


class RegistrationDetailOut(Schema):
    id: int
    status: str
    match_token: str
    created_at: str
    attendee_first_name: str
    attendee_last_name: str
    attendee_email: str
    attendee_phone: str
    attendee_gender: str
    attendee_age: int
    attendee_experience: str
    attending_coaching: bool
    attending_happy_hour: bool


class EventStatsOut(Schema):
    total_registrations: int
    confirmed: int
    pending: int
    waitlisted: int
    male_count: int
    female_count: int
    revenue: int


class LoginIn(Schema):
    username: str
    password: str


class MatchFormAttendeeOut(Schema):
    registration_id: int
    display_name: str  # "First L."


class MatchFormDataOut(Schema):
    event_title: str
    event_date: datetime
    attendee_name: str  # greeting name for the viewer
    attendees: list[MatchFormAttendeeOut]
    already_submitted: bool = False
    previous_selections: list[int] = []  # registration IDs if reopened


class MatchFormSubmissionIn(Schema):
    selected_ids: list[int]


class MatchOut(Schema):
    id: int
    attendee_a_name: str
    attendee_b_name: str
    notified: bool
    created_at: str


class MatchSubmissionOut(Schema):
    id: int
    submitted_by_name: str
    submitted_by_gender: str
    selected_names: list[str]
    submitted_at: str


class TriggerOut(Schema):
    detail: str


class SubscribeIn(Schema):
    email: str
