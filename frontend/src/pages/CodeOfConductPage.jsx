import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';

function CodeOfConductPage() {
  const sectionStyle = { mb: 5 };
  const headingStyle = { mb: 2 };

  return (
    <>
      {/* Hero Banner */}
      <Box
        sx={{
          background: 'linear-gradient(135deg, #f8e1e8 0%, #fdf8f6 100%)',
          py: 8,
          textAlign: 'center',
        }}
      >
        <Container maxWidth="md">
          <Typography variant="h3" component="h1" gutterBottom>
            Code of Conduct
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ maxWidth: 600, mx: 'auto' }}>
            Our guidelines for a safe, respectful, and fun experience
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: 8 }}>
        {/* Our Commitment */}
        <Box sx={sectionStyle}>
          <Typography variant="h4" sx={headingStyle}>
            Our Commitment
          </Typography>
          <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
            Pickleball Singles Social is committed to creating a safe, welcoming, and
            respectful environment for all attendees. Everyone deserves to enjoy the event
            without feeling uncomfortable, pressured, or unsafe. We take this seriously and
            ask that all participants do the same.
          </Typography>
        </Box>

        {/* Expected Behavior */}
        <Box sx={sectionStyle}>
          <Typography variant="h4" sx={headingStyle}>
            Expected Behavior
          </Typography>
          <Box component="ul" sx={{ pl: 3, color: 'text.secondary', lineHeight: 2.2 }}>
            <li>Be respectful and kind to all attendees, staff, and venue employees</li>
            <li>Accept "no" gracefully, whether on the court or off it</li>
            <li>Respect personal space and boundaries at all times</li>
            <li>Be a good sport: encourage others, play fair, and keep it fun</li>
            <li>Welcome newcomers and help them feel included</li>
          </Box>
        </Box>

        {/* Unacceptable Behavior */}
        <Box sx={sectionStyle}>
          <Typography variant="h4" sx={headingStyle}>
            Unacceptable Behavior
          </Typography>
          <Box component="ul" sx={{ pl: 3, color: 'text.secondary', lineHeight: 2.2 }}>
            <li>Harassment, intimidation, or discriminatory language of any kind</li>
            <li>Unwanted physical contact or invasion of personal space</li>
            <li>Pressuring anyone to share personal contact information</li>
            <li>Attending while visibly intoxicated or becoming intoxicated during the event</li>
            <li>Disruptive behavior that interferes with others' enjoyment</li>
          </Box>
        </Box>

        {/* Reporting */}
        <Box sx={sectionStyle}>
          <Typography variant="h4" sx={headingStyle}>
            Reporting
          </Typography>
          <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
            If you experience or witness behavior that violates this Code of Conduct, please
            speak with the event organizer on-site. They will be clearly identified at every
            event. If you prefer to report after the event, you can reach us at{' '}
            <Box component="span" sx={{ fontWeight: 600, color: 'text.primary' }}>
              info@pickleballsinglessocial.com
            </Box>
            . All reports will be handled with discretion.
          </Typography>
        </Box>

        {/* Consequences */}
        <Box sx={sectionStyle}>
          <Typography variant="h4" sx={headingStyle}>
            Consequences
          </Typography>
          <Typography color="text.secondary" sx={{ lineHeight: 1.8 }}>
            The organizer reserves the right to remove any attendee who violates this Code of
            Conduct at any time, without warning. Attendees removed for conduct violations
            will not receive a refund. Repeated violations may result in being banned from
            future events.
          </Typography>
        </Box>
      </Container>
    </>
  );
}

export default CodeOfConductPage;
