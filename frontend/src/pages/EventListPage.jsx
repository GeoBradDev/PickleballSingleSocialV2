import { useEffect } from 'react';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardActions from '@mui/material/CardActions';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import CircularProgress from '@mui/material/CircularProgress';
import { Link as RouterLink } from 'react-router';
import useEventsStore from '../stores/eventsStore.js';

function getStatusChip(event) {
  const registered = (event.male_count || 0) + (event.female_count || 0);
  const remaining = event.capacity - registered;
  const percentFull = registered / event.capacity;

  if (remaining <= 0) {
    return <Chip label="Sold Out" color="error" size="small" />;
  }
  if (percentFull >= 0.85) {
    return <Chip label="Filling Fast" color="warning" size="small" />;
  }
  return <Chip label="Open" color="success" size="small" />;
}

function EventListPage() {
  const { events, loading, fetchEvents } = useEventsStore();

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  if (loading) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress color="primary" />
        <Typography sx={{ mt: 2 }} color="text.secondary">Loading events...</Typography>
      </Container>
    );
  }

  if (!loading && events.length === 0) {
    return (
      <>
        <Box
          sx={{
            background: 'linear-gradient(135deg, #f8e1e8 0%, #fdf8f6 100%)',
            py: 8,
            textAlign: 'center',
          }}
        >
          <Container maxWidth="md">
            <Typography variant="h3" component="h1" gutterBottom>
              Upcoming Events
            </Typography>
          </Container>
        </Box>
        <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            No upcoming events right now
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3 }}>
            New events are added regularly. Subscribe to get notified!
          </Typography>
          <Button variant="contained" component={RouterLink} to="/#subscribe">
            Get Notified
          </Button>
        </Container>
      </>
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
    <>
      <Box
        sx={{
          background: 'linear-gradient(135deg, #f8e1e8 0%, #fdf8f6 100%)',
          py: 8,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" component="h1" gutterBottom>
            Upcoming Events
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Find your next event and register today
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {events.map((event) => {
            const spotsRemaining =
              event.capacity - (event.male_count || 0) - (event.female_count || 0);
            return (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={event.id}>
                <Card
                  elevation={0}
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                      <Typography variant="h5" gutterBottom sx={{ mb: 0 }}>
                        {event.title}
                      </Typography>
                      {getStatusChip(event)}
                    </Box>
                    <Typography color="text.secondary" sx={{ mb: 1 }}>
                      {formatDate(event.event_date)}
                    </Typography>
                    <Chip
                      label={`Ages ${event.age_label}`}
                      size="small"
                      sx={{ backgroundColor: 'primary.light', mb: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary">
                      {spotsRemaining > 0
                        ? `${spotsRemaining} spots remaining`
                        : 'Event full'}
                    </Typography>
                  </CardContent>
                  <CardActions sx={{ px: 2, pb: 2 }}>
                    <Button
                      variant="contained"
                      fullWidth
                      component={RouterLink}
                      to={`/events/${event.id}/register`}
                      disabled={spotsRemaining <= 0}
                    >
                      Register
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Container>
    </>
  );
}

export default EventListPage;
