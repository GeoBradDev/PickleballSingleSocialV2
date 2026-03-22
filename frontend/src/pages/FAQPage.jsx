import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

const faqs = [
  {
    question: 'Do I need to know how to play pickleball?',
    answer:
      'Not at all! Every event starts with a 30-minute coaching session where our volunteers cover the basics. Whether you have never held a paddle or you play every weekend, our events are designed for all skill levels.',
  },
  {
    question: "What if I don't have a partner?",
    answer:
      "That is the whole point! You will be paired with different partners throughout the event during mixed doubles play. Our format ensures you get to meet and play with multiple people.",
  },
  {
    question: 'Is this a dating event?',
    answer:
      'Pickleball Singles Social is a social event for single people. Whether you are looking for romance, friendship, or just a fun afternoon, our events create a relaxed atmosphere for genuine connections. There is no pressure to match with anyone. Some people come just for the pickleball.',
  },
  {
    question: 'What is the refund policy?',
    answer:
      'We offer full refunds up to 48 hours before the event. Within 48 hours, we can transfer your registration to the next event. No-shows are not eligible for refunds.',
  },
  {
    question: 'What should I bring?',
    answer:
      'Just yourself and comfortable athletic clothes and shoes! We provide all pickleball equipment including paddles and balls. If you have your own paddle, feel free to bring it. We also recommend bringing a water bottle to stay hydrated.',
  },
  {
    question: 'What are the age groups?',
    answer:
      'We currently offer two age groups: 25-45 and 45+. Each event is specific to one age group so you are meeting people in a similar life stage. Check the Events page to find the right group for you.',
  },
  {
    question: 'How does the matching work?',
    answer:
      'After the event, you will receive a private link where you can select the people you would like to connect with. If someone you selected also selected you (a mutual match), we will share contact information between you both. Your selections are completely private and only mutual matches are revealed.',
  },
  {
    question: 'Will I feel comfortable coming alone?',
    answer:
      'Absolutely. Coming alone is the norm, not the exception — that is the whole point of the event. Every event is capped at 32 people with a guaranteed balanced gender ratio, so the room always feels right. Our volunteer organizers are on-site the entire time to make sure everyone feels welcome, and the coached format means you are never just standing around awkwardly. The rotating play structure ensures you are always with someone new.',
  },
  {
    question: 'What if the ratio becomes unbalanced?',
    answer:
      'We close registration for one gender as soon as it fills to maintain a balanced ratio. If the balance shifts due to last-minute cancellations, we fill from a waitlist to keep things even. We take this seriously because a balanced event is a better experience for everyone.',
  },
  {
    question: 'Where are events held?',
    answer:
      'All events are held indoors at Arch Pickleball in Bridgeton, Missouri. Playing indoors means every event runs rain or shine with no weather cancellations. Parking is free and the facility is easy to find.',
  },
  {
    question: 'What happens after the event?',
    answer:
      'After the on-court session wraps up at 5 PM, the group heads to a nearby spot for happy hour. It is a great chance to keep the conversations going in a relaxed setting. Later that evening you will receive a private link to submit your matches. Select the people you would like to connect with and if the feeling is mutual, we will share contact details with both of you the following morning.',
  },
];

function FAQPage() {
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
            Frequently Asked Questions
          </Typography>
          <Typography variant="h6" color="text.secondary">
            Everything you need to know before your first event
          </Typography>
        </Container>
      </Box>

      <Container maxWidth="md" sx={{py: 6}}>
        {faqs.map((faq, index) => (
          <Accordion
            key={index}
            elevation={0}
            sx={{
              mb: 1,
              border: '1px solid',
              borderColor: 'divider',
              '&:before': {display: 'none'},
            }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon/>}>
              <Typography variant="h6" sx={{fontSize: '1.05rem', fontWeight: 500}}>
                {faq.question}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography color="text.secondary">{faq.answer}</Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Container>
    </>
  );
}

export default FAQPage;
