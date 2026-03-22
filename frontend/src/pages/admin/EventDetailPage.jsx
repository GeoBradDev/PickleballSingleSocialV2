import { useState, useEffect } from 'react';
import { useParams, Link as RouterLink } from 'react-router';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Alert from '@mui/material/Alert';
import {
  fetchEventStats,
  fetchEventRegistrations,
  fetchEventMatches,
  fetchEventMatchSubmissions,
  triggerCommand,
} from '../../api.js';

function EventDetailPage() {
  const { eventId } = useParams();
  const [stats, setStats] = useState(null);
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  // Matches tab state
  const [matches, setMatches] = useState([]);
  const [matchesLoading, setMatchesLoading] = useState(false);
  const [matchesLoaded, setMatchesLoaded] = useState(false);
  const [commandAlert, setCommandAlert] = useState(null);
  const [commandLoading, setCommandLoading] = useState(false);

  // Submissions tab state
  const [submissions, setSubmissions] = useState([]);
  const [submissionsLoading, setSubmissionsLoading] = useState(false);
  const [submissionsLoaded, setSubmissionsLoaded] = useState(false);

  useEffect(() => {
    Promise.all([
      fetchEventStats(eventId),
      fetchEventRegistrations(eventId),
    ])
      .then(([statsData, regsData]) => {
        setStats(statsData);
        setRegistrations(regsData);
      })
      .finally(() => setLoading(false));
  }, [eventId]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);

    if (newValue === 1 && !matchesLoaded) {
      setMatchesLoading(true);
      fetchEventMatches(eventId)
        .then((data) => {
          setMatches(data);
          setMatchesLoaded(true);
        })
        .catch(() => setMatches([]))
        .finally(() => setMatchesLoading(false));
    }

    if (newValue === 2 && !submissionsLoaded) {
      setSubmissionsLoading(true);
      fetchEventMatchSubmissions(eventId)
        .then((data) => {
          setSubmissions(data);
          setSubmissionsLoaded(true);
        })
        .catch(() => setSubmissions([]))
        .finally(() => setSubmissionsLoading(false));
    }
  };

  const handleTriggerCommand = async (command) => {
    setCommandLoading(true);
    setCommandAlert(null);
    try {
      const result = await triggerCommand(eventId, command);
      setCommandAlert({ severity: 'success', message: result.message || `${command} completed successfully.` });
      // Refresh matches after a command
      fetchEventMatches(eventId)
        .then((data) => setMatches(data))
        .catch(() => {});
    } catch (err) {
      setCommandAlert({ severity: 'error', message: err.message || `${command} failed.` });
    } finally {
      setCommandLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  const statCards = [
    { label: 'Total', value: stats?.total ?? 0 },
    { label: 'Confirmed', value: stats?.confirmed ?? 0 },
    { label: 'Male', value: stats?.male ?? 0 },
    { label: 'Female', value: stats?.female ?? 0 },
    { label: 'Revenue', value: `$${stats?.revenue ?? 0}` },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Button component={RouterLink} to="/admin" sx={{ mb: 2 }}>
        Back to Dashboard
      </Button>
      <Typography variant="h4" component="h1" gutterBottom>
        Event Details
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={handleTabChange}>
          <Tab label="Registrations" />
          <Tab label="Matches" />
          <Tab label="Submissions" />
        </Tabs>
      </Box>

      {/* Registrations Tab */}
      {activeTab === 0 && (
        <>
          <Box sx={{ display: 'flex', gap: 2, mb: 4, flexWrap: 'wrap' }}>
            {statCards.map((card) => (
              <Card key={card.label} sx={{ minWidth: 140 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    {card.label}
                  </Typography>
                  <Typography variant="h5">{card.value}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>

          <Typography variant="h5" gutterBottom>
            Registrations
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Gender</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Registered Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {registrations.map((reg) => (
                  <TableRow key={reg.id}>
                    <TableCell>{reg.first_name} {reg.last_name}</TableCell>
                    <TableCell>{reg.email}</TableCell>
                    <TableCell>{reg.phone}</TableCell>
                    <TableCell>{reg.gender}</TableCell>
                    <TableCell>{reg.status}</TableCell>
                    <TableCell>{new Date(reg.created_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
                {registrations.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} sx={{ textAlign: 'center' }}>
                      No registrations yet.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      {/* Matches Tab */}
      {activeTab === 1 && (
        <>
          <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
            <Button
              variant="contained"
              onClick={() => handleTriggerCommand('process-matches')}
              disabled={commandLoading}
            >
              Process Matches
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => handleTriggerCommand('send-match-emails')}
              disabled={commandLoading}
            >
              Send Match Emails
            </Button>
          </Box>

          {commandAlert && (
            <Alert severity={commandAlert.severity} sx={{ mb: 2 }} onClose={() => setCommandAlert(null)}>
              {commandAlert.message}
            </Alert>
          )}

          {matchesLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Person A</TableCell>
                    <TableCell>Person B</TableCell>
                    <TableCell>Notified</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {matches.map((match) => (
                    <TableRow key={match.id}>
                      <TableCell>{match.person_a_name}</TableCell>
                      <TableCell>{match.person_b_name}</TableCell>
                      <TableCell>{match.notified ? 'Yes' : 'No'}</TableCell>
                      <TableCell>{new Date(match.created_at).toLocaleDateString()}</TableCell>
                    </TableRow>
                  ))}
                  {matches.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ textAlign: 'center' }}>
                        No matches yet.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}

      {/* Submissions Tab */}
      {activeTab === 2 && (
        <>
          {submissionsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Submitted By</TableCell>
                    <TableCell>Gender</TableCell>
                    <TableCell>Selected</TableCell>
                    <TableCell>Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {submissions.map((sub) => (
                    <TableRow key={sub.id}>
                      <TableCell>{sub.submitted_by_name}</TableCell>
                      <TableCell>{sub.gender}</TableCell>
                      <TableCell>{sub.selected_name}</TableCell>
                      <TableCell>{new Date(sub.created_at).toLocaleDateString()}</TableCell>
                    </TableRow>
                  ))}
                  {submissions.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={4} sx={{ textAlign: 'center' }}>
                        No submissions yet.
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}
    </Box>
  );
}

export default EventDetailPage;
