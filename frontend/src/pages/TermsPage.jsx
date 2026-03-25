import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import { Link as RouterLink } from 'react-router';

function TermsPage() {
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
            Terms of Service
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: March 25, 2026
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: 6 }}>
        <Typography variant="h5" gutterBottom>
          Agreement to Terms
        </Typography>
        <Typography sx={{ mb: 3 }}>
          By accessing or using the Pickleball Singles Social website and services, you agree
          to be bound by these Terms of Service. If you do not agree to these terms, please do
          not use our services.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Eligibility
        </Typography>
        <Typography sx={{ mb: 3 }}>
          You must be at least 18 years old to use our services or register for events. Each
          event has a designated age range, and you must fall within that range to register. By
          registering, you confirm that the information you provide (including age and gender) is
          accurate.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Event Registration and Payment
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography>Registration is on a first-come, first-served basis, subject to capacity and gender balance limits.</Typography></li>
          <li><Typography>Payment is required at the time of registration to confirm your spot.</Typography></li>
          <li><Typography>All payments are processed securely through Stripe.</Typography></li>
          <li><Typography>Pricing may vary by gender to help maintain balanced attendance. Current pricing is displayed during registration.</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Refund Policy
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography><strong>Full refund:</strong> Available up to 48 hours before the event.</Typography></li>
          <li><Typography><strong>Within 48 hours:</strong> Refunds are at our discretion and may be issued as credit toward a future event.</Typography></li>
          <li><Typography><strong>No-shows:</strong> No refunds for no-shows.</Typography></li>
          <li><Typography><strong>Event cancellation:</strong> If we cancel an event, all registrants will receive a full refund.</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Waitlist
        </Typography>
        <Typography sx={{ mb: 3 }}>
          If an event is full, you may be placed on a waitlist. If a spot opens up, you will be
          notified by email with a payment link. Waitlist spots are offered on a first-come,
          first-served basis and must be claimed promptly. We are not obligated to hold a spot
          indefinitely.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Code of Conduct
        </Typography>
        <Typography sx={{ mb: 3 }}>
          All attendees must adhere to our{' '}
          <Link component={RouterLink} to="/code-of-conduct">Code of Conduct</Link>.
          We reserve the right to remove any participant who violates these guidelines without a
          refund. We are committed to providing a safe, respectful, and inclusive environment at
          every event.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Matching and Contact Sharing
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography>After each event, attendees may optionally submit a match form indicating who they would like to connect with.</Typography></li>
          <li><Typography>Contact information (name and email) is shared only between mutual matches, where both parties selected each other.</Typography></li>
          <li><Typography>The match form has a deadline. Submissions after the deadline will not be processed.</Typography></li>
          <li><Typography>We are not responsible for interactions between matched individuals after contact information is shared.</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Assumption of Risk
        </Typography>
        <Typography sx={{ mb: 3 }}>
          Pickleball is a physical activity that carries inherent risks of injury. By
          registering for an event, you acknowledge and accept these risks. You agree to
          participate at your own risk and release Pickleball Singles Social, its organizers,
          volunteers, and venue partners from any liability for injuries sustained during events.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Intellectual Property
        </Typography>
        <Typography sx={{ mb: 3 }}>
          All content on this website, including text, graphics, logos, and software, is the
          property of Pickleball Singles Social and is protected by applicable intellectual
          property laws. You may not reproduce, distribute, or create derivative works without
          our written consent.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Limitation of Liability
        </Typography>
        <Typography sx={{ mb: 3 }}>
          To the fullest extent permitted by law, Pickleball Singles Social shall not be liable
          for any indirect, incidental, special, consequential, or punitive damages arising
          from your use of our services or attendance at our events.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Changes to Terms
        </Typography>
        <Typography sx={{ mb: 3 }}>
          We reserve the right to modify these Terms of Service at any time. Changes will be
          posted on this page with an updated date. Continued use of our services after changes
          are posted constitutes acceptance of the revised terms.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Governing Law
        </Typography>
        <Typography sx={{ mb: 3 }}>
          These Terms of Service are governed by and construed in accordance with the laws of the
          State of Missouri, without regard to its conflict of law provisions.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Contact Us
        </Typography>
        <Typography sx={{ mb: 1 }}>
          If you have questions about these Terms of Service, please contact us at:
        </Typography>
        <Typography sx={{ mb: 3 }}>
          <Link href="mailto:info@pickleballsinglessocial.com">info@pickleballsinglessocial.com</Link>
        </Typography>
      </Container>
    </>
  );
}

export default TermsPage;
