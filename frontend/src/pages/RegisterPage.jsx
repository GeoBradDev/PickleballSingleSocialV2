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

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    gender: '',
    age_group: '',
    contact_preference: 'email',
  });

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
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const result = await registerForEvent(eventId, formData);
      setClientSecret(result.client_secret);
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
            {formatDate(event.date)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Age Group: {event.age_group}
          </Typography>
        </Paper>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {clientSecret ? (
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
              required
              fullWidth
            />
            <TextField
              label="Phone"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
              fullWidth
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
            <FormControl fullWidth required>
              <InputLabel>Age Group</InputLabel>
              <Select
                name="age_group"
                value={formData.age_group}
                onChange={handleChange}
                label="Age Group"
              >
                <MenuItem value="25-45">25-45</MenuItem>
                <MenuItem value="45+">45+</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth>
              <InputLabel>Contact Preference</InputLabel>
              <Select
                name="contact_preference"
                value={formData.contact_preference}
                onChange={handleChange}
                label="Contact Preference"
              >
                <MenuItem value="email">Email</MenuItem>
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="both">Both</MenuItem>
              </Select>
            </FormControl>
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
