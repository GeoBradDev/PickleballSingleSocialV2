import { Routes, Route } from 'react-router';
import Nav from './components/Nav.jsx';
import Footer from './components/Footer.jsx';
import HomePage from './pages/HomePage.jsx';
import EventListPage from './pages/EventListPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import SuccessPage from './pages/SuccessPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import FAQPage from './pages/FAQPage.jsx';
import CodeOfConductPage from './pages/CodeOfConductPage.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import LoginPage from './pages/admin/LoginPage.jsx';
import DashboardPage from './pages/admin/DashboardPage.jsx';
import EventDetailPage from './pages/admin/EventDetailPage.jsx';
import EventFormPage from './pages/admin/EventFormPage.jsx';
import MatchFormPage from './pages/MatchFormPage.jsx';

function App() {
  return (
    <>
      <Nav />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/events" element={<EventListPage />} />
        <Route path="/events/:eventId/register" element={<RegisterPage />} />
        <Route path="/register/success" element={<SuccessPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/faq" element={<FAQPage />} />
        <Route path="/code-of-conduct" element={<CodeOfConductPage />} />
        <Route path="/match/:token" element={<MatchFormPage />} />
        <Route path="/admin/login" element={<LoginPage />} />
        <Route path="/admin" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/admin/events/new" element={<ProtectedRoute><EventFormPage /></ProtectedRoute>} />
        <Route path="/admin/events/:eventId" element={<ProtectedRoute><EventDetailPage /></ProtectedRoute>} />
        <Route path="/admin/events/:eventId/edit" element={<ProtectedRoute><EventFormPage /></ProtectedRoute>} />
      </Routes>
      <Footer />
    </>
  );
}

export default App;
