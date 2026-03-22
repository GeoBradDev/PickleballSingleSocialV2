import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import MenuItem from '@mui/material/MenuItem';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import { createEvent, updateEvent, fetchAdminEvents } from '../../api.js';

function EventFormPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(eventId);

  const [form, setForm] = useState({
    title: '',
    event_date: '',
    age_group: '25-45',
    capacity: '',
    status: 'draft',
  });
  const [loading, setLoading] = useState(isEdit);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isEdit) return;
    fetchAdminEvents()
      .then((events) => {
        const event = events.find((e) => String(e.id) === String(eventId));
        if (event) {
          setForm({
            title: event.title || '',
            event_date: event.event_date ? event.event_date.slice(0, 16) : '',
            age_group: event.age_group || '25-45',
            capacity: event.capacity ?? '',
            status: event.status || 'draft',
          });
        }
      })
      .finally(() => setLoading(false));
  }, [isEdit, eventId]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const data = { ...form, capacity: Number(form.capacity) };
      if (isEdit) {
        await updateEvent(eventId, data);
      } else {
        await createEvent(data);
      }
      navigate('/admin');
    } catch (err) {
      setError(err.message || 'Failed to save event');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
      <Card sx={{ maxWidth: 600, width: '100%' }}>
        <CardContent>
          <Typography variant="h5" component="h1" gutterBottom>
            {isEdit ? 'Edit Event' : 'Create Event'}
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Title"
              name="title"
              value={form.title}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Event Date"
              name="event_date"
              type="datetime-local"
              value={form.event_date}
              onChange={handleChange}
              required
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
              label="Age Group"
              name="age_group"
              value={form.age_group}
              onChange={handleChange}
              select
              required
              fullWidth
            >
              <MenuItem value="25-45">25-45</MenuItem>
              <MenuItem value="45+">45+</MenuItem>
            </TextField>
            <TextField
              label="Capacity"
              name="capacity"
              type="number"
              value={form.capacity}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Status"
              name="status"
              value={form.status}
              onChange={handleChange}
              select
              required
              fullWidth
            >
              <MenuItem value="draft">Draft</MenuItem>
              <MenuItem value="open">Open</MenuItem>
              <MenuItem value="closed">Closed</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
            </TextField>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Button type="submit" variant="contained" disabled={submitting}>
                {submitting ? 'Saving...' : 'Save'}
              </Button>
              <Button variant="outlined" onClick={() => navigate('/admin')}>
                Cancel
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default EventFormPage;
