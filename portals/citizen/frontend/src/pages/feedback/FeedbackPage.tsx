import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  MenuItem,
  Grid,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Chip,
  Rating,
  Divider,
  Pagination,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Feedback as FeedbackIcon,
  BugReport as ComplaintIcon,
  Lightbulb as SuggestionIcon,
  Star as RatingIcon,
  CheckCircle as ResolvedIcon,
  HourglassEmpty as PendingIcon,
  Cancel as ClosedIcon,
  Assignment as InProgressIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { feedbackService } from '@/services/feedback.service';
import { Feedback, FeedbackRequest, PagedResponse } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { isValidUUID } from '@/utils/uuidValidator';
import { applicationService } from '@/services/application.service';
import { ServiceApplication } from '@/types/api';
import { getFeedbackTypeLabel, getFeedbackCategoryLabel, getFeedbackStatusLabel } from '@/utils/localization';

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
      id={`feedback-tabpanel-${index}`}
      aria-labelledby={`feedback-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const FeedbackPage: React.FC = () => {
  const { t } = useTranslation();
  const { user, isAuthenticated, profileNotFound } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  const [tabValue, setTabValue] = useState(0); // 0: Submit, 1: History
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackHistory, setFeedbackHistory] = useState<Feedback[]>([]);
  const [applications, setApplications] = useState<ServiceApplication[]>([]);
  const [serviceRequests, setServiceRequests] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);
  const [selectedFeedback, setSelectedFeedback] = useState<Feedback | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const pageSize = 10;

  const [formData, setFormData] = useState<FeedbackRequest>({
    type: 'FEEDBACK',
    category: '',
    subject: '',
    message: '',
    rating: undefined,
    applicationId: undefined,
  });

  useEffect(() => {
    if (!isAuthenticated) {
      setError(t('feedback.notAuthenticated', { defaultValue: 'You must be logged in to submit feedback.' }));
      return;
    }

    if (profileNotFound || !user?.id || !isValidUUID(user.id)) {
      setError(t('feedback.profileNeeded', { defaultValue: 'Please complete your profile before submitting feedback.' }));
      return;
    }

    if (tabValue === 1) {
      loadFeedbackHistory();
    }
    loadApplications();
    loadServiceRequests();
  }, [user?.id, isAuthenticated, profileNotFound, tabValue, page]);

  const loadFeedbackHistory = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response: PagedResponse<Feedback> = await feedbackService.getFeedbackByCitizen(
        user.id,
        page,
        pageSize
      );
      setFeedbackHistory(response.content || []);
      setTotalPages(response.totalPages || 0);
      setTotalElements(response.totalElements || 0);
    } catch (err: any) {
      console.error('Failed to load feedback history:', err);
      // Handle 500 errors gracefully - backend might not be fully implemented
      if (err.response?.status === 500) {
        setFeedbackHistory([]);
        setTotalPages(0);
        setTotalElements(0);
        // Don't show error message for 500 - just show empty state
        setError(null);
      } else {
        const errorMessage = err.response?.data?.message || t('feedback.loadFailed', { defaultValue: 'Failed to load feedback history' });
        setError(errorMessage);
        showError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadApplications = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      return;
    }

    try {
      const response = await applicationService.getApplicationsByCitizen(user.id, 0, 50);
      setApplications(response.content || []);
    } catch (err) {
      console.error('Failed to load applications:', err);
      // Don't show error, just continue without application dropdown
    }
  };

  const loadServiceRequests = () => {
    try {
      const storedRequests = localStorage.getItem('serviceRequests');
      if (storedRequests) {
        const requests = JSON.parse(storedRequests);
        setServiceRequests(requests || []);
      }
    } catch (err) {
      console.error('Failed to load service requests:', err);
      setServiceRequests([]);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0); // Reset to first page when switching tabs
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value - 1); // MUI Pagination is 1-based, API is 0-based
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleRatingChange = (_event: React.SyntheticEvent, newValue: number | null) => {
    setFormData((prev) => ({ ...prev, rating: newValue || undefined }));
  };

  const validateForm = () => {
    if (!formData.message || formData.message.trim().length === 0) {
      setError(t('feedback.errors.messageRequired', { defaultValue: 'Message is required.' }));
      return false;
    }
    if (formData.type === 'RATING' && !formData.rating) {
      setError(t('feedback.errors.ratingRequired', { defaultValue: 'Rating is required for rating type feedback.' }));
      return false;
    }
    setError(null);
    return true;
  };

  const handleSubmit = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      setError(t('feedback.errors.invalidCitizenId', { defaultValue: 'Invalid Citizen ID. Cannot submit feedback.' }));
      return;
    }

    if (!validateForm()) {
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Handle service request IDs (prefixed with 'sr-')
      let applicationId: string | undefined = formData.applicationId;
      if (applicationId && applicationId.startsWith('sr-')) {
        // For service requests, we can store the ID but the backend doesn't support it yet
        // For now, we'll just send undefined and let the backend handle it
        applicationId = undefined;
      }

      const submitData: FeedbackRequest = {
        type: formData.type,
        category: formData.category || undefined,
        subject: formData.subject || undefined,
        message: formData.message,
        rating: formData.rating,
        applicationId: applicationId,
      };

      console.log('Submitting feedback:', { citizenId: user.id, submitData });
      await feedbackService.submitFeedback(user.id, submitData);
      showSuccess(t('feedback.submitSuccess', { defaultValue: 'Feedback submitted successfully!' }));
      
      // Reset form
      setFormData({
        type: 'FEEDBACK',
        category: '',
        subject: '',
        message: '',
        rating: undefined,
        applicationId: undefined,
      });
      
      // Switch to history tab and refresh
      setTabValue(1);
      loadFeedbackHistory();
    } catch (err: any) {
      console.error('Feedback submission error:', err);
      // Handle 500 errors gracefully - backend might not be fully implemented
      if (err.response?.status === 500) {
        // Show a more user-friendly message for 500 errors
        const errorMessage = t('feedback.submitFailed', { defaultValue: 'Failed to submit feedback. The service may be temporarily unavailable. Please try again later.' });
        setError(errorMessage);
        showError(errorMessage);
      } else {
        const errorMessage = err.response?.data?.message || t('feedback.submitFailed', { defaultValue: 'Failed to submit feedback.' });
        setError(errorMessage);
        showError(errorMessage);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleViewDetails = (feedback: Feedback) => {
    setSelectedFeedback(feedback);
    setDetailDialogOpen(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'RESOLVED':
        return <ResolvedIcon color="success" fontSize="small" />;
      case 'IN_PROGRESS':
        return <InProgressIcon color="info" fontSize="small" />;
      case 'CLOSED':
        return <ClosedIcon color="default" fontSize="small" />;
      default:
        return <PendingIcon color="warning" fontSize="small" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'RESOLVED':
        return 'success';
      case 'IN_PROGRESS':
        return 'info';
      case 'CLOSED':
        return 'default';
      default:
        return 'warning';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'COMPLAINT':
        return <ComplaintIcon />;
      case 'SUGGESTION':
        return <SuggestionIcon />;
      case 'RATING':
        return <RatingIcon />;
      default:
        return <FeedbackIcon />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading && tabValue === 1 && feedbackHistory.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error && !isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('feedback.title', { defaultValue: 'Feedback & Complaints' })}
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={getTypeIcon(formData.type)}
            iconPosition="start"
            label={t('feedback.submitFeedback', { defaultValue: 'Submit Feedback' })}
          />
          <Tab
            icon={<FeedbackIcon />}
            iconPosition="start"
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('feedback.history', { defaultValue: 'My Feedback' })}
                {totalElements > 0 && (
                  <Chip label={totalElements} size="small" sx={{ height: 20 }} />
                )}
              </Box>
            }
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ maxWidth: 800, mx: 'auto' }}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                {error}
              </Alert>
            )}

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  select
                  label={t('feedback.type', { defaultValue: 'Feedback Type' })}
                  name="type"
                  value={formData.type}
                  onChange={handleInputChange}
                  fullWidth
                  required
                >
                  <MenuItem value="FEEDBACK">
                    {t('feedback.type.feedback', { defaultValue: 'General Feedback' })}
                  </MenuItem>
                  <MenuItem value="COMPLAINT">
                    {t('feedback.type.complaint', { defaultValue: 'Complaint' })}
                  </MenuItem>
                  <MenuItem value="SUGGESTION">
                    {t('feedback.type.suggestion', { defaultValue: 'Suggestion' })}
                  </MenuItem>
                  <MenuItem value="RATING">
                    {t('feedback.type.rating', { defaultValue: 'Rating' })}
                  </MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  select
                  label={t('feedback.category', { defaultValue: 'Category (Optional)' })}
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  fullWidth
                >
                  <MenuItem value="">{t('common.none', { defaultValue: 'None' })}</MenuItem>
                  <MenuItem value="APPLICATION">{t('feedback.category.application', { defaultValue: 'Application' })}</MenuItem>
                  <MenuItem value="SCHEME">{t('feedback.category.scheme', { defaultValue: 'Scheme' })}</MenuItem>
                  <MenuItem value="DOCUMENT">{t('feedback.category.document', { defaultValue: 'Document' })}</MenuItem>
                  <MenuItem value="PAYMENT">{t('feedback.category.payment', { defaultValue: 'Payment' })}</MenuItem>
                  <MenuItem value="SERVICE">{t('feedback.category.service', { defaultValue: 'Service' })}</MenuItem>
                  <MenuItem value="OTHER">{t('feedback.category.other', { defaultValue: 'Other' })}</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} sm={6}>
                <TextField
                  label={t('feedback.relatedApplication', { defaultValue: 'Related Application / Service Request (Optional)' })}
                  name="applicationId"
                  select
                  value={formData.applicationId || ''}
                  onChange={(e) => {
                    const value = e.target.value;
                    console.log('Related Application/Service Request selected:', { value, applications: applications.length, serviceRequests: serviceRequests.length });
                    setFormData((prev) => ({ ...prev, applicationId: value || undefined }));
                  }}
                  fullWidth
                >
                  <MenuItem value="">{t('common.none', { defaultValue: 'None' })}</MenuItem>
                  {applications.length > 0 && (
                    <MenuItem disabled sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                      {t('payments.applications', { defaultValue: 'Applications' })}
                    </MenuItem>
                  )}
                  {applications.map((app) => (
                    <MenuItem key={app.id} value={app.id}>
                      {app.applicationNumber || app.id.substring(0, 8)} - {app.subject || app.serviceType}
                    </MenuItem>
                  ))}
                  {serviceRequests.length > 0 && (
                    <MenuItem disabled sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                      {t('payments.serviceRequests', { defaultValue: 'Service Requests' })}
                    </MenuItem>
                  )}
                  {serviceRequests.map((sr) => {
                    const menuValue = `sr-${String(sr.id)}`;
                    return (
                      <MenuItem key={`sr-${String(sr.id)}`} value={menuValue}>
                        {sr.requestNumber} - {sr.name || sr.serviceName || 'Service Request'}
                      </MenuItem>
                    );
                  })}
                  {applications.length === 0 && serviceRequests.length === 0 && (
                    <MenuItem value="" disabled>
                      {t('feedback.noRelatedItems', { defaultValue: 'No applications or service requests found' })}
                    </MenuItem>
                  )}
                </TextField>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  label={t('feedback.subject', { defaultValue: 'Subject (Optional)' })}
                  name="subject"
                  value={formData.subject}
                  onChange={handleInputChange}
                  fullWidth
                  placeholder={t('feedback.subjectPlaceholder', { defaultValue: 'Brief summary of your feedback' })}
                />
              </Grid>

              {formData.type === 'RATING' && (
                <Grid item xs={12}>
                  <Box>
                    <Typography component="legend" sx={{ mb: 1 }}>
                      {t('feedback.rating', { defaultValue: 'Rating' })} *
                    </Typography>
                    <Rating
                      name="rating"
                      value={formData.rating || 0}
                      onChange={handleRatingChange}
                      size="large"
                    />
                  </Box>
                </Grid>
              )}

              <Grid item xs={12}>
                <TextField
                  label={t('feedback.message', { defaultValue: 'Message' })}
                  name="message"
                  value={formData.message}
                  onChange={handleInputChange}
                  fullWidth
                  multiline
                  rows={6}
                  required
                  error={!!error && !formData.message}
                  helperText={t('feedback.messageHelper', { defaultValue: 'Please provide detailed feedback, complaint, or suggestion (max 5000 characters)' })}
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                  <Button
                    variant="outlined"
                    onClick={() => {
                      setFormData({
                        type: 'FEEDBACK',
                        category: '',
                        subject: '',
                        message: '',
                        rating: undefined,
                        applicationId: undefined,
                      });
                      setError(null);
                    }}
                    disabled={submitting}
                  >
                    {t('common.clear', { defaultValue: 'Clear' })}
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleSubmit}
                    disabled={submitting || !formData.message}
                    startIcon={getTypeIcon(formData.type)}
                  >
                    {submitting
                      ? t('common.submitting', { defaultValue: 'Submitting...' })
                      : t('feedback.submit', { defaultValue: 'Submit Feedback' })}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : feedbackHistory.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <FeedbackIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('feedback.noFeedback', { defaultValue: 'No feedback submitted yet' })}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {t('feedback.noFeedbackDescription', { defaultValue: 'Your feedback history will appear here once you submit feedback.' })}
              </Typography>
            </Box>
          ) : (
            <>
              <Grid container spacing={2}>
                {feedbackHistory.map((feedback) => (
                  <Grid item xs={12} key={feedback.id}>
                    <Card
                      variant="outlined"
                      sx={{
                        cursor: 'pointer',
                        '&:hover': {
                          boxShadow: 3,
                        },
                      }}
                      onClick={() => handleViewDetails(feedback)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {getTypeIcon(feedback.type)}
                            <Typography variant="h6" component="div">
                              {feedback.subject || getFeedbackTypeLabel(feedback.type, t)}
                            </Typography>
                          </Box>
                          <Chip
                            label={getFeedbackStatusLabel(feedback.status, t)}
                            size="small"
                            color={getStatusColor(feedback.status) as any}
                            icon={getStatusIcon(feedback.status)}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {feedback.message.length > 150
                            ? feedback.message.substring(0, 150) + '...'
                            : feedback.message}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2 }}>
                          {feedback.rating && (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                              <Rating value={feedback.rating} readOnly size="small" />
                            </Box>
                          )}
                          {feedback.category && (
                            <Chip label={getFeedbackCategoryLabel(feedback.category, t)} size="small" variant="outlined" />
                          )}
                          <Typography variant="caption" color="text.secondary">
                            {formatDate(feedback.createdAt)}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
                  <Pagination
                    count={totalPages}
                    page={page + 1}
                    onChange={handlePageChange}
                    color="primary"
                    size="large"
                  />
                </Box>
              )}
            </>
          )}
        </TabPanel>
      </Paper>

      {/* Feedback Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {selectedFeedback && getTypeIcon(selectedFeedback.type)}
            <Typography variant="h6">
              {selectedFeedback?.subject || selectedFeedback?.type}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedFeedback && (
            <Box>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    {t('feedback.type', { defaultValue: 'Type' })}
                  </Typography>
                  <Typography variant="body1">{getFeedbackTypeLabel(selectedFeedback.type, t)}</Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    {t('feedback.status', { defaultValue: 'Status' })}
                  </Typography>
                  <Chip
                    label={getFeedbackStatusLabel(selectedFeedback.status, t)}
                    size="small"
                    color={getStatusColor(selectedFeedback.status) as any}
                    icon={getStatusIcon(selectedFeedback.status)}
                  />
                </Grid>
                {selectedFeedback.category && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      {t('feedback.category', { defaultValue: 'Category' })}
                    </Typography>
                    <Typography variant="body1">{getFeedbackCategoryLabel(selectedFeedback.category, t)}</Typography>
                  </Grid>
                )}
                {selectedFeedback.rating && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary">
                      {t('feedback.rating', { defaultValue: 'Rating' })}
                    </Typography>
                    <Rating value={selectedFeedback.rating} readOnly />
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Typography variant="subtitle2" color="text.secondary">
                    {t('feedback.message', { defaultValue: 'Message' })}
                  </Typography>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {selectedFeedback.message}
                  </Typography>
                </Grid>
                {selectedFeedback.resolution && (
                  <Grid item xs={12}>
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="subtitle2" color="text.secondary">
                      {t('feedback.resolution', { defaultValue: 'Resolution' })}
                    </Typography>
                    <Alert severity="info" sx={{ mt: 1 }}>
                      {selectedFeedback.resolution}
                    </Alert>
                    {selectedFeedback.resolvedAt && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                        {t('feedback.resolvedOn', { defaultValue: 'Resolved on' })}: {formatDate(selectedFeedback.resolvedAt)}
                      </Typography>
                    )}
                  </Grid>
                )}
                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="caption" color="text.secondary">
                    {t('feedback.submittedOn', { defaultValue: 'Submitted on' })}: {formatDate(selectedFeedback.createdAt)}
                  </Typography>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>
            {t('common.close', { defaultValue: 'Close' })}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Message Dialog */}
      <MessageDialog
        open={dialog.open}
        onClose={close}
        type={dialog.type}
        message={dialog.message}
        title={dialog.title}
        autoClose={dialog.type === 'success'}
        autoCloseDelay={3000}
      />
    </Container>
  );
};

