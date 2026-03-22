import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { Link as RouterLink } from 'react-router';

function SuccessPage() {
  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
        <CheckCircleOutlineIcon
          color="primary"
          sx={{ fontSize: 64, mb: 2 }}
        />
        <Typography variant="h4" gutterBottom>
          Registration Confirmed!
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 4 }}>
          Thank you for registering! You will receive a confirmation email shortly.
        </Typography>
        <Button
          variant="contained"
          size="large"
          component={RouterLink}
          to="/"
        >
          Back to Home
        </Button>
      </Paper>
    </Container>
  );
}

export default SuccessPage;
