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
    event_date: '',
    min_age: 25,
    max_age: '',
    capacity: 32,
    max_male_ratio: 0.55,
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
            event_date: event.event_date ? event.event_date.slice(0, 16) : '',
            min_age: event.min_age ?? 25,
            max_age: event.max_age ?? '',
            capacity: event.capacity ?? 32,
            max_male_ratio: event.max_male_ratio ?? 0.55,
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
      const data = {
        ...form,
        min_age: Number(form.min_age),
        max_age: form.max_age === '' ? null : Number(form.max_age),
        capacity: Number(form.capacity),
        max_male_ratio: Number(form.max_male_ratio),
      };
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
              label="Event Date"
              name="event_date"
              type="datetime-local"
              value={form.event_date}
              onChange={handleChange}
              required
              fullWidth
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Min Age"
                name="min_age"
                type="number"
                value={form.min_age}
                onChange={handleChange}
                required
                fullWidth
              />
              <TextField
                label="Max Age"
                name="max_age"
                type="number"
                value={form.max_age}
                onChange={handleChange}
                fullWidth
                helperText="Leave blank for no upper limit"
              />
            </Box>
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
              label="Max Male Ratio"
              name="max_male_ratio"
              type="number"
              value={form.max_male_ratio}
              onChange={handleChange}
              required
              fullWidth
              helperText="e.g. 0.55 means max 55% male"
              slotProps={{ htmlInput: { min: 0, max: 1, step: 0.05 } }}
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
