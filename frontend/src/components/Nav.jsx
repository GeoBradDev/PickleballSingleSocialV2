import { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import MenuIcon from '@mui/icons-material/Menu';
import { Link as RouterLink } from 'react-router';

const navLinks = [
  { label: 'Home', to: '/' },
  { label: 'Events', to: '/events' },
  { label: 'About', to: '/about' },
  { label: 'FAQ', to: '/faq' },
];

function Nav() {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <AppBar
      position="sticky"
      sx={{
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(8px)',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        <Box
          component={RouterLink}
          to="/"
          sx={{ display: 'flex', alignItems: 'center', textDecoration: 'none' }}
        >
          <Box
            component="img"
            src="/small_logo.png"
            alt="Pickleball Singles Social"
            sx={{ height: 50 }}
          />
        </Box>

        <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
          {navLinks.map((link) => (
            <Button
              key={link.to}
              component={RouterLink}
              to={link.to}
              sx={{ color: 'text.primary', fontWeight: 500 }}
            >
              {link.label}
            </Button>
          ))}
        </Box>

        <IconButton
          sx={{ display: { xs: 'flex', md: 'none' }, color: 'text.primary' }}
          onClick={() => setDrawerOpen(true)}
        >
          <MenuIcon />
        </IconButton>

        <Drawer
          anchor="right"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        >
          <Box sx={{ width: 250, pt: 2 }}>
            <List>
              {navLinks.map((link) => (
                <ListItem key={link.to} disablePadding>
                  <ListItemButton
                    component={RouterLink}
                    to={link.to}
                    onClick={() => setDrawerOpen(false)}
                  >
                    <ListItemText primary={link.label} />
                  </ListItemButton>
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>
      </Toolbar>
    </AppBar>
  );
}

export default Nav;
