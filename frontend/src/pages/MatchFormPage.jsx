import { useState, useEffect } from 'react';
import { useParams } from 'react-router';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import { fetchMatchFormData, submitMatchForm } from '../api.js';

function MatchFormPage() {
  const { token } = useParams();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [closed, setClosed] = useState(false);
  const [selected, setSelected] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    fetchMatchFormData(token)
      .then((result) => {
        setData(result);
        if (result.already_submitted) {
          setSelected(result.previous_selections || []);
          setSubmitted(true);
        }
        setLoading(false);
      })
      .catch((err) => {
        if (err.message === 'CLOSED') {
          setClosed(true);
        } else {
          setError(err.message);
        }
        setLoading(false);
      });
  }, [token]);

  function handleToggle(regId) {
    setSelected((prev) =>
      prev.includes(regId)
        ? prev.filter((id) => id !== regId)
        : [...prev, regId]
    );
  }

  async function handleSubmit() {
    setSubmitting(true);
    try {
      await submitMatchForm(token, selected);
      setSubmitted(true);
    } catch (err) {
      if (err.message === 'ALREADY_SUBMITTED') {
        setSubmitted(true);
      } else if (err.message === 'CLOSED') {
        setClosed(true);
      } else {
        setError(err.message);
      }
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

  if (closed) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            Match Form Closed
          </Typography>
          <Typography color="text.secondary">
            The match form for this event has closed. Matches are being processed.
          </Typography>
        </Paper>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="sm" sx={{ py: 8 }}>
        <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h5" gutterBottom>
            Invalid Link
          </Typography>
          <Typography color="text.secondary">
            This match form link is invalid or has expired.
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="sm" sx={{ py: 4 }}>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          {data.event_title}
        </Typography>
        <Typography color="text.secondary" gutterBottom>
          {data.event_date}
        </Typography>
        <Typography sx={{ mb: 3 }}>
          Hi {data.attendee_name}! Select the people you would like to connect with:
        </Typography>

        {submitted ? (
          <>
            <Alert severity="success" sx={{ mb: 2 }}>
              Your selections have been submitted! You will be notified of any mutual matches.
            </Alert>
            <Typography variant="subtitle2" gutterBottom>
              Your selections:
            </Typography>
            {data.attendees
              .filter((a) => selected.includes(a.registration_id))
              .map((a) => (
                <Typography key={a.registration_id} variant="body2">
                  {a.display_name}
                </Typography>
              ))}
          </>
        ) : (
          <>
            <FormGroup>
              {data.attendees.map((attendee) => (
                <FormControlLabel
                  key={attendee.registration_id}
                  control={
                    <Checkbox
                      color="primary"
                      checked={selected.includes(attendee.registration_id)}
                      onChange={() => handleToggle(attendee.registration_id)}
                    />
                  }
                  label={attendee.display_name}
                />
              ))}
            </FormGroup>
            {data.attendees.length === 0 && (
              <Typography color="text.secondary">
                No attendees to display.
              </Typography>
            )}
            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handleSubmit}
              disabled={submitting || selected.length === 0}
              sx={{ mt: 3 }}
            >
              {submitting ? 'Submitting...' : 'Submit Selections'}
            </Button>
          </>
        )}
      </Paper>
    </Container>
  );
}

export default MatchFormPage;
