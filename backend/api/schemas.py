from ninja import Schema


class EventOut(Schema):
    id: int
    title: str
    age_group: str
    event_date: str
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
    age_group: str
    contact_preference: str = "email"


class RegistrationOut(Schema):
    id: int
    status: str
    match_token: str


class PaymentIntentOut(Schema):
    client_secret: str
    registration_id: int


class ErrorOut(Schema):
    detail: str


class EventIn(Schema):
    title: str
    age_group: str
    event_date: str
    capacity: int = 32
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
    attendee_contact_preference: str


class EventStatsOut(Schema):
    total_registrations: int
    confirmed: int
    pending: int
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
    event_date: str
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
