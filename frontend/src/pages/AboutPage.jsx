import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import GroupsIcon from '@mui/icons-material/Groups';
import FavoriteIcon from '@mui/icons-material/Favorite';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import {Link} from "@mui/material";

function AboutPage() {
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
            About Pickleball Singles Social
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{maxWidth: 600, mx: 'auto'}}>
            Where singles meet through the fastest-growing sport in America
          </Typography>
        </Container>
      </Box>

      {/* The Story */}
      <Container maxWidth="md" sx={{py: 6}}>
        <Typography variant="h4" gutterBottom>
          Our Story
        </Typography>
        <Typography sx={{mb: 2}}>
          Pickleball Singles Social was born out of a simple idea: what if meeting someone
          new could feel as natural as playing a game together? We saw how pickleball was
          bringing people of all backgrounds together on the court, and we thought, why not
          create an event that combines the fun of the sport with the excitement of meeting
          someone special?
        </Typography>
        <Typography sx={{mb: 2}}>
          Our events are designed to be low-pressure, high-fun experiences. Whether you have
          never picked up a paddle or you are a seasoned player, our coached format ensures
          everyone has a great time. No awkward silences, no forced conversation starters,
          just genuine connection through play.
        </Typography>
        <Typography>
          We believe the best relationships start with shared experiences. That is why every
          event includes coaching, mixed doubles play, and a post-game happy hour so you can
          get to know your matches off the court too.
        </Typography>
      </Container>

      {/* Values */}
      <Box sx={{backgroundColor: 'primary.light', py: 6}}>
        <Container maxWidth="md">
          <Typography variant="h4" gutterBottom sx={{textAlign: 'center', mb: 4}}>
            What We Stand For
          </Typography>
          <Grid container spacing={3}>
            <Grid size={{xs: 12, md: 4}}>
              <Card elevation={0} sx={{height: '100%', textAlign: 'center', p: 2}}>
                <CardContent>
                  <AttachMoneyIcon sx={{fontSize: 48, color: 'secondary.main', mb: 2}}/>
                  <Typography variant="h5" gutterBottom>
                    Affordable
                  </Typography>
                  <Typography color="text.secondary">
                    Quality events without the premium price tag. We keep costs low so
                    everyone can join the fun.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{xs: 12, md: 4}}>
              <Card elevation={0} sx={{height: '100%', textAlign: 'center', p: 2}}>
                <CardContent>
                  <GroupsIcon sx={{fontSize: 48, color: 'secondary.main', mb: 2}}/>
                  <Typography variant="h5" gutterBottom>
                    Inclusive
                  </Typography>
                  <Typography color="text.secondary">
                    No experience needed. All skill levels, backgrounds, and ages are
                    welcome at our events.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{xs: 12, md: 4}}>
              <Card elevation={0} sx={{height: '100%', textAlign: 'center', p: 2}}>
                <CardContent>
                  <FavoriteIcon sx={{fontSize: 48, color: 'secondary.main', mb: 2}}/>
                  <Typography variant="h5" gutterBottom>
                    Community-Focused
                  </Typography>
                  <Typography color="text.secondary">
                    Building real connections, not just swiping. We create spaces where
                    genuine relationships can grow.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Organizer Section */}
      <Container maxWidth="md" sx={{py: 6}}>
        <Typography variant="h4" gutterBottom>
          Organized by Gateway Smash
        </Typography>
        <Typography sx={{mb: 2}}>
          Pickleball Singles Social is brought to you by Gateway Smash, a grassroots, volunteer-run pickleball community
          based in St. Louis.
        </Typography>

        <Typography sx={{ mb: 2 }}>
          Gateway Smash was built by players who were tired of corporate leagues that charged too much and delivered too
          little. The idea was simple: create something affordable, well-organized, and genuinely player-first. No
          profits, no fluff — every dollar collected goes directly toward court rental. Today, Gateway Smash runs
          seasonal indoor ladder leagues every Sunday night at Arch Pickleball in Bridgeton.
        </Typography>

        <Typography sx={{ mb: 2 }}>
          Pickleball Singles Social grew out of watching that community come alive on the court. Strangers becoming
          regulars, regulars becoming friends. The sport has a way of breaking down walls faster than any icebreaker,
          and we wanted to create a dedicated space for singles to experience that too.
        </Typography>

        <Typography sx={{ mb: 2 }}>
          Every event is volunteer-run, personally organized, and built with the same values that drive everything
          Gateway Smash does: keep it affordable, keep it inclusive, and make it genuinely fun.
        </Typography>

        <Link
          href="https://www.gatewaysmash.com"
          target="_blank"
          rel="noopener noreferrer"
          sx={{mt: 2, display: 'inline-block'}}
        >
          Learn more about Gateway Smash →
        </Link>
      </Container>

      {/* Trust Section */}
      <Box sx={{backgroundColor: 'background.default', py: 6}}>
        <Container maxWidth="md" sx={{textAlign: 'center'}}>
          <VerifiedUserIcon sx={{fontSize: 48, color: 'primary.main', mb: 2}}/>
          <Typography variant="h4" gutterBottom>
            Your Safety and Comfort Come First
          </Typography>
          <Typography color="text.secondary" sx={{maxWidth: 600, mx: 'auto'}}>
            We maintain balanced gender ratios at every event, provide on-site coaching so
            no one feels lost, and our matching system ensures your contact information is
            only shared with mutual matches. You are always in control of who you connect with.
          </Typography>
        </Container>
      </Box>
    </>
  );
}

export default AboutPage;
