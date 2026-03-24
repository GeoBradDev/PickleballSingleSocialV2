import { useState, useEffect } from 'react';
import { useParams } from 'react-router';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { fetchEvent, registerForEvent } from '../api.js';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');

function PaymentForm() {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [paymentError, setPaymentError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!stripe || !elements) return;

    setProcessing(true);
    setPaymentError(null);

    const result = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/register/success`,
      },
    });

    if (result.error) {
      setPaymentError(result.error.message);
      setProcessing(false);
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <PaymentElement />
      {paymentError && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {paymentError}
        </Alert>
      )}
      <Button
        type="submit"
        variant="contained"
        fullWidth
        size="large"
        disabled={!stripe || processing}
        sx={{ mt: 3 }}
      >
        {processing ? 'Processing...' : 'Pay Now'}
      </Button>
    </Box>
  );
}

function RegisterPage() {
  const { eventId } = useParams();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [clientSecret, setClientSecret] = useState(null);
  const [waitlisted, setWaitlisted] = useState(false);

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    gender: '',
    age: '',
    experience: 'none',
    attending_coaching: false,
    attending_happy_hour: false,
  });

  const [fieldErrors, setFieldErrors] = useState({});

  function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function validatePhone(phone) {
    const digits = phone.replace(/\D/g, '');
    return digits.length >= 10 && digits.length <= 15;
  }

  function formatPhone(value) {
    const digits = value.replace(/\D/g, '');
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
  }

  function handleBlur(e) {
    const { name, value } = e.target;
    if (name === 'email' && value && !validateEmail(value)) {
      setFieldErrors((prev) => ({ ...prev, email: 'Enter a valid email address' }));
    } else if (name === 'email') {
      setFieldErrors((prev) => ({ ...prev, email: null }));
    }
    if (name === 'phone' && value && !validatePhone(value)) {
      setFieldErrors((prev) => ({ ...prev, phone: 'Enter a valid 10-digit phone number' }));
    } else if (name === 'phone') {
      setFieldErrors((prev) => ({ ...prev, phone: null }));
    }
  }

  useEffect(() => {
    fetchEvent(eventId)
      .then((data) => {
        setEvent(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [eventId]);

  function handleChange(e) {
    const { name, value, type, checked } = e.target;
    if (name === 'phone') {
      setFormData((prev) => ({ ...prev, phone: formatPhone(value) }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: type === 'checkbox' ? checked : value,
      }));
    }
    if (fieldErrors[name]) {
      setFieldErrors((prev) => ({ ...prev, [name]: null }));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();

    const errors = {};
    if (!validateEmail(formData.email)) errors.email = 'Enter a valid email address';
    if (!validatePhone(formData.phone)) errors.phone = 'Enter a valid 10-digit phone number';
    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await registerForEvent(eventId, { ...formData, age: Number(formData.age) });
      if (result.status === 'waitlisted') {
        setWaitlisted(true);
      } else {
        setClientSecret(result.client_secret);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      {event && (
        <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            {event.title}
          </Typography>
          <Typography color="text.secondary">
            {formatDate(event.event_date)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Ages {event.age_label}
          </Typography>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {waitlisted ? (
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            You're on the Waitlist
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Thanks for signing up! We keep the group intentionally small and balanced.
            You're on the waitlist, and if a spot opens up, we'll email you right away
            with a link to complete payment.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Keep an eye on your inbox at <strong>{formData.email}</strong>.
          </Typography>
        </Paper>
      ) : clientSecret ? (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Payment
          </Typography>
          <Elements stripe={stripePromise} options={{ clientSecret }}>
            <PaymentForm />
          </Elements>
        </Paper>
      ) : (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h5" gutterBottom>
            Registration
          </Typography>
          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              required
              fullWidth
            />
            <TextField
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              onBlur={handleBlur}
              required
              fullWidth
              error={Boolean(fieldErrors.email)}
              helperText={fieldErrors.email}
            />
            <TextField
              label="Phone"
              name="phone"
              type="tel"
              value={formData.phone}
              onChange={handleChange}
              onBlur={handleBlur}
              required
              fullWidth
              placeholder="(555) 123-4567"
              error={Boolean(fieldErrors.phone)}
              helperText={fieldErrors.phone}
            />
            <Box
              sx={{
                mt: 1,
                p: 1.5,
                backgroundColor: 'primary.light',
                borderRadius: 2,
                textAlign: 'center',
              }}
            >
              <Typography variant="body2" color="text.primary">
                Pricing: $15 for women, $20 for men
              </Typography>
            </Box>
            <FormControl fullWidth required>
              <InputLabel>Gender</InputLabel>
              <Select
                name="gender"
                value={formData.gender}
                onChange={handleChange}
                label="Gender"
              >
                <MenuItem value="male">Male ($20)</MenuItem>
                <MenuItem value="female">Female ($15)</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Age"
              name="age"
              type="number"
              value={formData.age}
              onChange={handleChange}
              required
              fullWidth
              helperText={event ? `This event is for ages ${event.age_label}` : ''}
              slotProps={{ htmlInput: { min: 18, max: 120 } }}
            />
            <FormControl fullWidth required>
              <InputLabel>Pickleball Experience</InputLabel>
              <Select
                name="experience"
                value={formData.experience}
                onChange={handleChange}
                label="Pickleball Experience"
              >
                <MenuItem value="none">Never played</MenuItem>
                <MenuItem value="beginner">Beginner (played a few times)</MenuItem>
                <MenuItem value="intermediate">Intermediate (play regularly)</MenuItem>
                <MenuItem value="advanced">Advanced (competitive)</MenuItem>
              </Select>
            </FormControl>
            <FormControlLabel
              control={
                <Checkbox
                  name="attending_coaching"
                  checked={formData.attending_coaching}
                  onChange={handleChange}
                />
              }
              label="I plan to attend the beginner coaching session (2:30 PM)"
            />
            <FormControlLabel
              control={
                <Checkbox
                  name="attending_happy_hour"
                  checked={formData.attending_happy_hour}
                  onChange={handleChange}
                />
              }
              label="I plan to attend the happy hour after the event"
            />
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={submitting}
              sx={{ mt: 1 }}
            >
              {submitting ? 'Submitting...' : 'Continue to Payment'}
            </Button>
          </Box>
        </Paper>
      )}
    </Container>
  );
}

export default RegisterPage;
