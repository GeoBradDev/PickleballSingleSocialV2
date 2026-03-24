const API_BASE = import.meta.env.VITE_API_URL || '';

export async function fetchEvents() {
  const res = await fetch(`${API_BASE}/api/events/`);
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function fetchEvent(id) {
  const res = await fetch(`${API_BASE}/api/events/${id}/`);
  if (!res.ok) throw new Error('Failed to fetch event');
  return res.json();
}

export async function registerForEvent(eventId, data) {
  const res = await fetch(`${API_BASE}/api/events/${eventId}/register/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Registration failed');
  }
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/api/auth/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
}

export async function logout() {
  const res = await fetch(`${API_BASE}/api/auth/logout/`, {
    method: 'POST',
    credentials: 'include',
  });
  return res.json();
}

export async function fetchMe() {
  const res = await fetch(`${API_BASE}/api/auth/me/`, {
    credentials: 'include',
  });
  if (!res.ok) return null;
  return res.json();
}

export async function fetchAdminEvents() {
  const res = await fetch(`${API_BASE}/api/admin/events/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch events');
  return res.json();
}

export async function createEvent(data) {
  const res = await fetch(`${API_BASE}/api/admin/events/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create event');
  return res.json();
}

export async function updateEvent(id, data) {
  const res = await fetch(`${API_BASE}/api/admin/events/${id}/`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to update event');
  return res.json();
}

export async function deleteEvent(id) {
  const res = await fetch(`${API_BASE}/api/admin/events/${id}/`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to delete event');
}

export async function fetchEventRegistrations(eventId) {
  const res = await fetch(`${API_BASE}/api/admin/events/${eventId}/registrations/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch registrations');
  return res.json();
}

export async function fetchEventStats(eventId) {
  const res = await fetch(`${API_BASE}/api/admin/events/${eventId}/stats/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchMatchFormData(token) {
  const res = await fetch(`${API_BASE}/api/match-form/${token}/`);
  if (res.status === 410) throw new Error('CLOSED');
  if (!res.ok) throw new Error('Invalid or expired link');
  return res.json();
}

export async function submitMatchForm(token, selectedIds) {
  const res = await fetch(`${API_BASE}/api/match-form/${token}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ selected_ids: selectedIds }),
  });
  if (res.status === 409) throw new Error('ALREADY_SUBMITTED');
  if (res.status === 410) throw new Error('CLOSED');
  if (!res.ok) throw new Error('Submission failed');
  return res.json();
}

export async function fetchEventMatches(eventId) {
  const res = await fetch(`${API_BASE}/api/admin/events/${eventId}/matches/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch matches');
  return res.json();
}

export async function fetchEventMatchSubmissions(eventId) {
  const res = await fetch(`${API_BASE}/api/admin/events/${eventId}/match-submissions/`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch submissions');
  return res.json();
}

export async function fetchRegistrationPayment(registrationId) {
  const res = await fetch(`${API_BASE}/api/registrations/${registrationId}/payment/`);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to fetch payment info');
  }
  return res.json();
}

export async function subscribeEmail(email) {
  const res = await fetch(`${API_BASE}/api/subscribe/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) throw new Error('Subscribe failed');
  return res.json();
}

export async function triggerCommand(eventId, command) {
  const res = await fetch(`${API_BASE}/api/admin/events/${eventId}/trigger/${command}/`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to trigger command');
  return res.json();
}
