from ninja.security import SessionAuth


class StaffSessionAuth(SessionAuth):
    """Session-based auth that also requires is_staff."""

    def authenticate(self, request, key=None):
        if request.user.is_authenticated and request.user.is_staff:
            return request.user
        return None


staff_auth = StaffSessionAuth()
