import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Box } from '@mui/material';

import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

// Public Pages
import LoginPage from './pages/auth/LoginPage';
import TermsAndConditions from './pages/TermsAndConditions';
import Sitemap from './pages/Sitemap';

// Protected Pages
import DashboardPage from './pages/dashboard/DashboardPage';
import SchemesBrowsePage from './pages/schemes/SchemesBrowsePage';
import SchemeDetailsPage from './pages/schemes/SchemeDetailsPage';
import EligibilityCheckerPage from './pages/schemes/EligibilityCheckerPage';
import ApplicationsHubPage from './pages/applications/ApplicationsHubPage';
import ApplicationDetailPage from './pages/applications/ApplicationDetailPage';
import ApplicationSubmissionPage from './pages/applications/ApplicationSubmissionPage';
import { DocumentsPage } from './pages/documents/DocumentsPage';
import ProfilePage from './pages/profile/ProfilePage';
import { ProfileDashboardPage } from './pages/profile/ProfileDashboardPage';
import { FamilyMemberProfilePage } from './pages/profile/FamilyMemberProfilePage';
import { BenefitsPage } from './pages/benefits/BenefitsPage';
import { NotificationsPage } from './pages/notifications/NotificationsPage';
import { FeedbackPage } from './pages/feedback/FeedbackPage';
import { ServicesPage } from './pages/services/ServicesPage';
import { HelpPage } from './pages/help/HelpPage';
import { SettingsPage } from './pages/settings/SettingsPage';
import { PaymentsPage } from './pages/payments/PaymentsPage';
import { SearchResultsPage } from './pages/search/SearchResultsPage';
import { ChatPage } from './pages/chat/ChatPage';

// Placeholder component for pages not yet implemented
const ComingSoon = () => {
  const { t } = useTranslation();
  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <h1>{t('common.comingSoon')}</h1>
      <p>This page is under development</p>
    </Box>
  );
};

const App: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/terms-conditions" element={<TermsAndConditions />} />
          <Route path="/sitemap" element={<Sitemap />} />

          {/* Protected Routes */}
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Schemes Routes */}
          <Route path="/schemes" element={<SchemesBrowsePage />} />
          <Route path="/schemes/browse" element={<SchemesBrowsePage />} />
          <Route path="/schemes/eligibility" element={<EligibilityCheckerPage />} />
          <Route path="/schemes/:schemeId" element={<SchemeDetailsPage />} />

          {/* Applications Routes */}
          <Route path="/applications" element={<ApplicationsHubPage />} />
          <Route path="/applications/submit" element={<ApplicationSubmissionPage />} />
          <Route path="/applications/submit/:schemeId" element={<ApplicationSubmissionPage />} />
          <Route path="/applications/:id" element={<ApplicationDetailPage />} />

          {/* Documents Routes */}
          <Route path="/documents" element={<DocumentsPage />} />

          {/* Profile Routes */}
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/profile/dashboard" element={<ProfileDashboardPage />} />
          <Route path="/profile/family/:memberId" element={<FamilyMemberProfilePage />} />

          {/* Benefits Routes */}
          <Route path="/benefits" element={<BenefitsPage />} />

          {/* Payments Routes */}
          <Route path="/payments" element={<PaymentsPage />} />

          {/* Notifications Routes */}
          <Route path="/notifications" element={<NotificationsPage />} />

          {/* Feedback Routes */}
          <Route path="/feedback" element={<FeedbackPage />} />

          {/* Services Routes */}
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/services/catalog" element={<ServicesPage />} />
          <Route path="/services/request" element={<ServicesPage />} />
          <Route path="/services/status" element={<ServicesPage />} />

          {/* Help & Support Routes */}
          <Route path="/help" element={<HelpPage />} />

          {/* Chat Routes */}
          <Route path="/chat" element={<ChatPage />} />

          {/* Settings Routes */}
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/settings/notifications" element={<SettingsPage />} />
          <Route path="/settings/opt-out" element={<SettingsPage />} />
          <Route path="/settings/account" element={<SettingsPage />} />

          {/* Search Routes */}
          <Route path="/search" element={<SearchResultsPage />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Box>
      <Footer />
    </Box>
  );
};

export default App;

