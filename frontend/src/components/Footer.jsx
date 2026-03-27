import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { Link as RouterLink } from 'react-router';

function Footer() {
  return (
    <Box
      component="footer"
      sx={{
        backgroundColor: 'primary.light',
        py: 5,
        px: 3,
        mt: 8,
        textAlign: 'center',
      }}
    >
      <Typography
        variant="h6"
        sx={{ fontFamily: '"Playfair Display", serif', mb: 2, color: 'text.primary' }}
      >
        Pickleball Singles Social
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 3 }}>
        <Button component={RouterLink} to="/about" sx={{ color: 'text.secondary' }}>
          About
        </Button>
        <Button component={RouterLink} to="/faq" sx={{ color: 'text.secondary' }}>
          FAQ
        </Button>
        <Button component={RouterLink} to="/events" sx={{ color: 'text.secondary' }}>
          Events
        </Button>
        <Button component={RouterLink} to="/code-of-conduct" sx={{ color: 'text.secondary' }}>
          Code of Conduct
        </Button>
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, mb: 3 }}>
        <Button component={RouterLink} to="/privacy" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
          Privacy Policy
        </Button>
        <Button component={RouterLink} to="/terms" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
          Terms of Service
        </Button>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        Questions or found a bug?{' '}
        <Box
          component="a"
          href="mailto:info@pickleballsinglessocial.com"
          sx={{ color: 'text.primary', textDecoration: 'underline' }}
        >
          info@pickleballsinglessocial.com
        </Box>
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
        All events hosted in partnership with Arch Pickleball & Badminton, 11333 Blake Dr, Bridgeton, MO 63044
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {new Date().getFullYear()} Pickleball Singles Social. All rights reserved.
      </Typography>
    </Box>
  );
}

export default Footer;
