import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { Link as RouterLink } from 'react-router';
import Link from '@mui/material/Link';

function PrivacyPolicyPage() {
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
            Privacy Policy
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Last updated: March 25, 2026
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{ py: 6 }}>
        <Typography variant="h5" gutterBottom>
          Introduction
        </Typography>
        <Typography sx={{ mb: 3 }}>
          Pickleball Singles Social ("we," "us," or "our") operates the website
          pickleballsinglessocial.com and related services. This Privacy Policy explains how we
          collect, use, disclose, and safeguard your information when you visit our website or
          register for our events.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Information We Collect
        </Typography>
        <Typography sx={{ mb: 1 }}>
          We collect information you provide directly to us, including:
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography>First and last name</Typography></li>
          <li><Typography>Email address</Typography></li>
          <li><Typography>Phone number</Typography></li>
          <li><Typography>Gender and age</Typography></li>
          <li><Typography>Pickleball experience level</Typography></li>
          <li><Typography>Payment information (processed securely by Stripe; we do not store card details)</Typography></li>
          <li><Typography>Match form selections (who you would like to connect with after an event)</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          How We Use Your Information
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography>To process event registrations and payments</Typography></li>
          <li><Typography>To maintain balanced gender ratios at events</Typography></li>
          <li><Typography>To facilitate mutual matching after events (your contact info is only shared with mutual matches)</Typography></li>
          <li><Typography>To send event confirmations, reminders, and related communications</Typography></li>
          <li><Typography>To send marketing emails about upcoming events (you can unsubscribe at any time)</Typography></li>
          <li><Typography>To improve our events and services</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Information Sharing
        </Typography>
        <Typography sx={{ mb: 1 }}>
          We do not sell, trade, or rent your personal information to third parties. We share
          your information only in the following circumstances:
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography><strong>Mutual matches:</strong> If you and another attendee both select each other on the post-event match form, we share your name and email address with that person only.</Typography></li>
          <li><Typography><strong>Payment processing:</strong> We use Stripe to process payments. Your payment information is handled directly by Stripe under their <Link href="https://stripe.com/privacy" target="_blank" rel="noopener noreferrer">privacy policy</Link>.</Typography></li>
          <li><Typography><strong>Email services:</strong> We use MailerLite and MailerSend to manage subscriber lists and send emails.</Typography></li>
          <li><Typography><strong>Legal requirements:</strong> We may disclose information if required by law or to protect our rights and safety.</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Data Security
        </Typography>
        <Typography sx={{ mb: 3 }}>
          We implement reasonable security measures to protect your personal information.
          However, no method of transmission over the Internet or electronic storage is 100%
          secure. We cannot guarantee absolute security.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Your Rights and Choices
        </Typography>
        <Box component="ul" sx={{ mb: 3, pl: 3 }}>
          <li><Typography><strong>Access and correction:</strong> You may request access to or correction of your personal information by contacting us.</Typography></li>
          <li><Typography><strong>Deletion:</strong> You may request deletion of your personal information. We will comply unless we have a legal obligation to retain it.</Typography></li>
          <li><Typography><strong>Marketing opt-out:</strong> You can unsubscribe from marketing emails at any time using the link in any email we send.</Typography></li>
          <li><Typography><strong>Match form:</strong> Participation in the post-event match form is entirely optional.</Typography></li>
        </Box>

        <Typography variant="h5" gutterBottom>
          Cookies
        </Typography>
        <Typography sx={{ mb: 3 }}>
          Our website uses essential cookies for authentication and session management. We do
          not use tracking cookies or third-party advertising cookies.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Children's Privacy
        </Typography>
        <Typography sx={{ mb: 3 }}>
          Our services are not directed to individuals under 18 years of age. We do not
          knowingly collect personal information from children.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Changes to This Policy
        </Typography>
        <Typography sx={{ mb: 3 }}>
          We may update this Privacy Policy from time to time. We will notify you of any
          material changes by posting the new policy on this page and updating the "Last
          updated" date.
        </Typography>

        <Typography variant="h5" gutterBottom>
          Contact Us
        </Typography>
        <Typography sx={{ mb: 1 }}>
          If you have questions about this Privacy Policy or your personal information, please contact us at:
        </Typography>
        <Typography sx={{ mb: 3 }}>
          <Link href="mailto:info@pickleballsinglessocial.com">info@pickleballsinglessocial.com</Link>
        </Typography>
      </Container>
    </>
  );
}

export default PrivacyPolicyPage;
