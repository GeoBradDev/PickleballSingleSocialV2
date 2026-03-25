import { useEffect } from 'react';
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
import useAdminEventStore from '../../stores/adminEventStore.js';

function EventDetailPage() {
  const { eventId } = useParams();
  const {
    stats,
    registrations,
    matches,
    submissions,
    loading,
    matchesLoading,
    submissionsLoading,
    commandLoading,
    commandAlert,
    activeTab,
    setActiveTab,
    setCommandAlert,
    loadEvent,
    loadMatches,
    loadSubmissions,
    triggerCommand,
    reset,
  } = useAdminEventStore();

  useEffect(() => {
    reset();
    loadEvent(eventId);
    return () => reset();
  }, [eventId, reset, loadEvent]);

  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
    if (newValue === 1) loadMatches(eventId);
    if (newValue === 2) loadSubmissions(eventId);
  };

  const handleTriggerCommand = (command) => {
    triggerCommand(eventId, command);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  const statCards = [
    { label: 'Total', value: stats?.total_registrations ?? 0 },
    { label: 'Confirmed', value: stats?.confirmed ?? 0 },
    { label: 'Male', value: stats?.male_count ?? 0 },
    { label: 'Female', value: stats?.female_count ?? 0 },
    { label: 'Revenue', value: `$${((stats?.revenue ?? 0) / 100).toFixed(2)}` },
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
                    <TableCell>{reg.attendee_first_name} {reg.attendee_last_name}</TableCell>
                    <TableCell>{reg.attendee_email}</TableCell>
                    <TableCell>{reg.attendee_phone}</TableCell>
                    <TableCell>{reg.attendee_gender}</TableCell>
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
                      <TableCell>{match.attendee_a_name}</TableCell>
                      <TableCell>{match.attendee_b_name}</TableCell>
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
                      <TableCell>{sub.submitted_by_gender}</TableCell>
                      <TableCell>{sub.selected_names?.join(', ')}</TableCell>
                      <TableCell>{new Date(sub.submitted_at).toLocaleDateString()}</TableCell>
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
