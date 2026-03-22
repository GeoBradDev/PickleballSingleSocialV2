import { useState, useEffect } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import TextField from '@mui/material/TextField';
import Alert from '@mui/material/Alert';
import SportsIcon from '@mui/icons-material/Sports';
import GroupsIcon from '@mui/icons-material/Groups';
import SportsTennisIcon from '@mui/icons-material/SportsTennis';
import LocalBarIcon from '@mui/icons-material/LocalBar';
import CheckIcon from '@mui/icons-material/Check';
import ShieldOutlinedIcon from '@mui/icons-material/ShieldOutlined';
import { Link as RouterLink } from 'react-router';
import { fetchEvents, subscribeEmail } from '../api.js';

function HomePage() {
  const [nextEvent, setNextEvent] = useState(null);
  const [email, setEmail] = useState('');
  const [subscribeStatus, setSubscribeStatus] = useState(null);
  const [subscribing, setSubscribing] = useState(false);

  useEffect(() => {
    fetchEvents()
      .then((events) => {
        if (events.length > 0) {
          setNextEvent(events[0]);
        }
      })
      .catch(() => {});
  }, []);

  async function handleSubscribe(e) {
    e.preventDefault();
    if (!email) return;
    setSubscribing(true);
    setSubscribeStatus(null);
    try {
      await subscribeEmail(email);
      setSubscribeStatus('success');
      setEmail('');
    } catch {
      setSubscribeStatus('error');
    } finally {
      setSubscribing(false);
    }
  }

  function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
    });
  }

  return (
    <>
      {/* Hero Section */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #f8e1e8 0%, #fdf8f6 50%, #f5e6d0 100%)',
          py: { xs: 4, md: 6 },
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Box
            component="img"
            src="/pickleballsinglessociallogonobackground.png"
            alt="Pickleball Singles Social"
            sx={{ height: { xs: 220, md: 340 }, mb: 2, borderRadius: '50%' }}
          />
          <Typography variant="h2" component="h1" gutterBottom>
            Meet someone new. Learn a sport. Have fun.
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ mb: 1, maxWidth: 520, mx: 'auto' }}
          >
            Social pickleball events for singles who want to connect through play,
            not just profiles.
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{ mb: 1, fontStyle: 'italic' }}
          >
            Come solo, play mixed doubles, meet someone.
          </Typography>
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{ mb: 4 }}
          >
            A local St. Louis event for single professionals 25-45 and 45+
          </Typography>
          {nextEvent && (
            <Box sx={{ mb: 3 }}>
              <Chip
                label={`Next event: ${formatDate(nextEvent.event_date)}`}
                sx={{ mr: 1, mb: 1, backgroundColor: 'white' }}
              />
              <Chip
                label={`Ages ${nextEvent.age_group}`}
                sx={{ mb: 1, backgroundColor: 'white' }}
              />
            </Box>
          )}
          <Button
            variant="contained"
            size="large"
            component={RouterLink}
            to={nextEvent ? `/events/${nextEvent.id}/register` : '/events'}
            sx={{ px: 5, py: 1.5, fontSize: '1.1rem' }}
          >
            Register Now
          </Button>
        </Container>
      </Box>

      {/* Format Explainer */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Typography variant="h3" sx={{ textAlign: 'center', mb: 5 }}>
          How It Works
        </Typography>
        <Grid container spacing={4}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <SportsIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Optional Coaching at 2:30
              </Typography>
              <Typography color="text.secondary">
                A quick lesson so everyone feels confident on the court, no experience needed. Totally optional.
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <GroupsIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Mixed Doubles 3-5 PM
              </Typography>
              <Typography color="text.secondary">
                Rotate through partners and get to know everyone through fun, casual play.
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <SportsTennisIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Equipment Provided
              </Typography>
              <Typography color="text.secondary">
                Paddles and balls are on us. Just show up in comfy clothes and sneakers.
              </Typography>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Box sx={{ textAlign: 'center' }}>
              <LocalBarIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Optional Happy Hour After
              </Typography>
              <Typography color="text.secondary">
                Continue the conversation off the court at a nearby spot. No pressure, totally optional.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

      {/* What This Is Not */}
      <Box sx={{ backgroundColor: 'primary.light', py: 6 }}>
        <Container maxWidth="md" sx={{ textAlign: 'center' }}>
          <Typography variant="h3" sx={{ mb: 3 }}>
            What This Is Not
          </Typography>
          <Typography
            variant="h6"
            color="text.secondary"
            sx={{ maxWidth: 640, mx: 'auto', lineHeight: 1.8 }}
          >
            This is not a speed dating event. There is no pressure to match with anyone.
            Some people come just for the pickleball.
          </Typography>
        </Container>
      </Box>

      {/* Safety & Vibe */}
      <Container maxWidth="md" sx={{ py: 8 }}>
        <Typography variant="h3" sx={{ textAlign: 'center', mb: 5 }}>
          Designed with your comfort in mind
        </Typography>
        <Grid container spacing={3}>
          {[
            'Every event is hosted by a real person, not an algorithm',
            'We cap registration at a balanced ratio and close one gender when it fills',
            'Small groups, 32 max, so it never feels overwhelming',
            'Your contact info is only shared with mutual matches. You are always in control.',
            'Full refund up to 48 hours before the event',
          ].map((point) => (
            <Grid size={{ xs: 12, sm: 6 }} key={point}>
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1.5 }}>
                <ShieldOutlinedIcon sx={{ color: 'primary.main', mt: 0.3, flexShrink: 0 }} />
                <Typography color="text.secondary" sx={{ lineHeight: 1.7 }}>
                  {point}
                </Typography>
              </Box>
            </Grid>
          ))}
        </Grid>
        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Button
            component={RouterLink}
            to="/code-of-conduct"
            variant="text"
            sx={{ textTransform: 'none', fontSize: '1rem' }}
          >
            Read our Code of Conduct
          </Button>
        </Box>
      </Container>

      {/* Testimonials */}
      <Box sx={{ backgroundColor: 'primary.light', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h3" sx={{ textAlign: 'center', mb: 5 }}>
            What People Are Saying
          </Typography>
          <Grid container spacing={3}>
            {[
              {
                quote:
                  'I was so nervous going alone, but the coaching session broke the ice perfectly. I matched with two amazing people!',
                name: 'Sarah',
                age: 32,
              },
              {
                quote:
                  "Best $15 I have ever spent on a date activity. Way more fun than sitting across from a stranger at a coffee shop.",
                name: 'Jessica',
                age: 28,
              },
              {
                quote:
                  "I had never played pickleball before and ended up having the best Saturday afternoon. Already signed up for the next one.",
                name: 'Michelle',
                age: 41,
              },
            ].map((testimonial, i) => (
              <Grid size={{ xs: 12, md: 4 }} key={i}>
                <Card elevation={0} sx={{ height: '100%', p: 1 }}>
                  <CardContent>
                    <Typography
                      sx={{ fontStyle: 'italic', mb: 2, color: 'text.secondary', lineHeight: 1.8 }}
                    >
                      "{testimonial.quote}"
                    </Typography>
                    <Typography variant="subtitle2" color="primary.main">
                      {testimonial.name}, {testimonial.age}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Container>
      </Box>

      {/* Pricing */}
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Typography variant="h3" sx={{ textAlign: 'center', mb: 5 }}>
          Simple, Fair Pricing
        </Typography>
        <Card
          elevation={0}
          sx={{
            textAlign: 'center',
            p: 4,
            border: '2px solid',
            borderColor: 'primary.main',
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: 3, mb: 3 }}>
              <Box>
                <Typography variant="h3" color="primary.main">$15</Typography>
                <Typography variant="h6">Women</Typography>
              </Box>
              <Typography variant="h5" color="text.secondary">/</Typography>
              <Box>
                <Typography variant="h3" color="primary.main">$20</Typography>
                <Typography variant="h6">Men</Typography>
              </Box>
            </Box>
            <Box sx={{ textAlign: 'left', maxWidth: 300, mx: 'auto' }}>
              {['Optional coaching session', 'Mixed doubles play', 'Equipment provided', 'Optional Happy Hour', 'Optional mutual matching form'].map(
                (item) => (
                  <Box key={item} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CheckIcon sx={{ color: 'primary.main', mr: 1, fontSize: 20 }} />
                    <Typography variant="body2">{item}</Typography>
                  </Box>
                )
              )}
            </Box>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mt: 3, fontStyle: 'italic' }}
            >
              The price difference helps us maintain balanced attendance.
            </Typography>
          </CardContent>
        </Card>
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ textAlign: 'center', mt: 3 }}
        >
          Limited to 32 attendees per event with balanced gender ratios.
        </Typography>
      </Container>

      {/* Email Opt-in */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #f5e6d0 0%, #f8e1e8 100%)',
          py: 8,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="sm">
          <Typography variant="h4" gutterBottom>
            Not ready yet? Stay in the loop.
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            Get notified about upcoming events in your area.
          </Typography>
          <Box
            component="form"
            onSubmit={handleSubscribe}
            sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}
          >
            <TextField
              type="email"
              placeholder="Your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              size="small"
              sx={{
                flex: 1,
                maxWidth: 320,
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                  borderRadius: 28,
                },
              }}
            />
            <Button
              type="submit"
              variant="contained"
              disabled={subscribing}
              sx={{ px: 3 }}
            >
              {subscribing ? 'Sending...' : 'Subscribe'}
            </Button>
          </Box>
          {subscribeStatus === 'success' && (
            <Alert severity="success" sx={{ mt: 2, maxWidth: 400, mx: 'auto' }}>
              You are on the list! We will keep you posted.
            </Alert>
          )}
          {subscribeStatus === 'error' && (
            <Alert severity="error" sx={{ mt: 2, maxWidth: 400, mx: 'auto' }}>
              Something went wrong. Please try again.
            </Alert>
          )}
        </Container>
      </Box>
    </>
  );
}

export default HomePage;
