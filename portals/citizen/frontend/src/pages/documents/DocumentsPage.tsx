import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Typography,
  Box,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Button,
} from '@mui/material';
import { DocumentUpload } from '@/components/documents/DocumentUpload';
import { DocumentList } from '@/components/documents/DocumentList';
import { documentService } from '@/services/document.service';
import { Document } from '@/types/api';
import { useSelector } from 'react-redux';
import { RootState } from '@/store';
import { Link } from 'react-router-dom';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`documents-tabpanel-${index}`}
      aria-labelledby={`documents-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const DocumentsPage: React.FC = () => {
  const { t } = useTranslation();
  const [tabValue, setTabValue] = useState(0);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated, profileNotFound } = useSelector((state: RootState) => state.auth);

  // Helper function to validate UUID
  const isValidUserId = (id: string): boolean => {
    return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
  };

  const loadDocuments = async () => {
    if (!user?.id || !isValidUserId(user.id)) {
      setError('Invalid user ID. Please log in again.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const docs = await documentService.getDocumentsByCitizen(user.id);
      setDocuments(docs);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only load documents if we have a valid user ID
    if (user?.id && isValidUserId(user.id)) {
      loadDocuments();
    } else {
      // If authenticated but no profile, set loading to false
      if (isAuthenticated && !user?.id) {
        setLoading(false);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, isAuthenticated]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleUploadSuccess = () => {
    loadDocuments();
    setTabValue(0); // Switch to documents list tab
  };

  // Check authentication first
  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          {t('documents.loginRequired', { defaultValue: 'Please log in to view your documents' })}
        </Alert>
      </Container>
    );
  }

  // If authenticated but no profile, show message but allow viewing page
  if (isAuthenticated && (!user?.id || !isValidUserId(user.id))) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {t('documents.title', { defaultValue: 'My Documents' })}
        </Typography>
        <Alert severity="info" sx={{ mt: 2 }}>
          {profileNotFound 
            ? t('documents.profileRequired', { defaultValue: 'Your profile needs to be created. Please complete your profile registration to upload and manage documents.' })
            : t('documents.profileNotFound', { defaultValue: 'User profile not found. Please complete your profile or contact support.' })}
        </Alert>
        <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', gap: 2 }}>
          <Typography variant="body1" color="text.secondary">
            {t('documents.profileMessage', { defaultValue: 'Once your profile is created, you will be able to upload and manage your documents here.' })}
          </Typography>
          <Button
            variant="contained"
            component={Link}
            to="/profile"
            sx={{ alignSelf: 'flex-start' }}
          >
            {t('documents.completeProfile', { defaultValue: 'Complete Your Profile' })}
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('documents.title', { defaultValue: 'My Documents' })}
      </Typography>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label={t('documents.myDocuments', { defaultValue: 'My Documents' })} />
          <Tab label={t('documents.uploadDocument', { defaultValue: 'Upload Document' })} />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : error ? (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        ) : (
          <DocumentList documents={documents} onDelete={loadDocuments} />
        )}
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <DocumentUpload
          citizenId={user.id}
          onUploadSuccess={handleUploadSuccess}
        />
      </TabPanel>
    </Container>
  );
};

