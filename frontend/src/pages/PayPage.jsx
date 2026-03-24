import { useState, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import { loadStripe } from '@stripe/stripe-js';
import { Elements, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';
import { fetchEvent, fetchRegistrationPayment } from '../api.js';

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

function PayPage() {
  const { eventId } = useParams();
  const [searchParams] = useSearchParams();
  const registrationId = searchParams.get('registration');

  const [event, setEvent] = useState(null);
  const [clientSecret, setClientSecret] = useState(null);
  const [amount, setAmount] = useState(null);
  const [loading, setLoading] = useState(!registrationId ? false : true);
  const [error, setError] = useState(!registrationId ? 'Missing registration ID.' : null);

  useEffect(() => {
    if (!registrationId) return;

    Promise.all([
      fetchEvent(eventId),
      fetchRegistrationPayment(registrationId),
    ])
      .then(([eventData, paymentData]) => {
        setEvent(eventData);
        setClientSecret(paymentData.client_secret);
        setAmount(paymentData.amount);
      })
      .catch((err) => {
        setError(err.message);
      })
      .finally(() => setLoading(false));
  }, [eventId, registrationId]);

  if (loading) {
    return (
      <Container maxWidth="sm" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Alert severity="error">{error}</Alert>
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
        </Paper>
      )}

      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Complete Your Payment
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          A spot opened up! Complete payment below to confirm your registration.
        </Typography>
        {amount && (
          <Typography variant="h6" color="primary.main" sx={{ mb: 2 }}>
            ${(amount / 100).toFixed(0)}
          </Typography>
        )}
        {clientSecret && (
          <Elements stripe={stripePromise} options={{ clientSecret }}>
            <PaymentForm />
          </Elements>
        )}
      </Paper>
    </Container>
  );
}

export default PayPage;