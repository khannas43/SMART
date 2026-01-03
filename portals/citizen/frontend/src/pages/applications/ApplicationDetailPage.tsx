import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Breadcrumbs,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Pending as PendingIcon,
  Schedule as ScheduleIcon,
  Description as DescriptionIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  LocalOffer as SchemeIcon,
  CalendarToday as CalendarIcon,
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  Timeline as TimelineIcon,
  History as HistoryIcon,
  Payment as PaymentIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@/store/hooks';
import { applicationService, schemeService, documentService, paymentService } from '@/services';
import { ServiceApplication, Scheme, Document, ApplicationStatusHistory } from '@/types/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import { DocumentUpload } from '@/components/documents/DocumentUpload';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

import { getSchemeName } from '@/utils/localization';

const ApplicationDetailPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, showInfo, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Application data
  const [application, setApplication] = useState<ServiceApplication | null>(null);
  const [scheme, setScheme] = useState<Scheme | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [statusHistory, setStatusHistory] = useState<ApplicationStatusHistory[]>([]);

  // Expanded sections
  const [expandedSection, setExpandedSection] = useState<string | false>('details');

  // WebSocket for real-time updates
  const { isConnected } = useWebSocket({
    topics: id ? [`/topic/application/${id}`] : [],
    onMessage: (message) => {
      // Handle real-time status update
      if (message.applicationId === id) {
        showSuccess(message.message || t('application.status.updated', { defaultValue: 'Application status updated' }));
        
        // Reload application details
        loadApplicationDetails();
      }
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
    autoConnect: !!id,
  });

  useEffect(() => {
    if (!id) {
      setError(t('application.error.invalidId', { defaultValue: 'Invalid application ID' }));
      setLoading(false);
      return;
    }

    loadApplicationDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  // Clear error when application loads successfully
  useEffect(() => {
    if (application) {
      // Always clear error if application exists, regardless of error state
      if (error) {
        console.log('Clearing error because application loaded successfully');
        setError(null);
      }
    }
  }, [application, error]);

  const loadApplicationDetails = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      // Load application (this is the critical call - if this fails, show error)
      console.log('Loading application with ID:', id);
      const appData = await applicationService.getApplicationById(id);
      console.log('Application loaded successfully:', appData?.applicationNumber);
      
      // Clear any previous errors and set application
      // Both state updates happen synchronously
      setError(null);
      setApplication(appData);
      
      console.log('Application state set, error cleared');

      // Load scheme if schemeId exists
      if (appData.schemeId) {
        try {
          const schemeData = await schemeService.getSchemeById(appData.schemeId);
          setScheme(schemeData);
        } catch (err) {
          console.warn('Could not load scheme:', err);
        }
      }

      // Load documents for this application
      try {
        const appDocs = await documentService.getDocumentsByApplication(id);
        setDocuments(appDocs);
      } catch (err: any) {
        // Only log if it's not a 404 (application might not have documents yet)
        if (err.response?.status !== 404) {
          console.warn('Could not load documents:', err);
        }
      }

      // Load status history (this will return empty array if endpoint fails)
      const historyData = await applicationService.getApplicationStatusHistory(id);
      if (historyData.length > 0) {
        setStatusHistory(historyData.reverse()); // Show most recent first
      } else {
        // Fallback: Build basic history from application data if no history endpoint
        const fallbackHistory: ApplicationStatusHistory[] = [];
        if (appData.submittedAt) {
          fallbackHistory.push({
            id: 'fallback-1',
            applicationId: appData.id,
            toStatus: 'SUBMITTED',
            changedAt: appData.submittedAt,
            comments: 'Application submitted',
          } as ApplicationStatusHistory);
        }
        if (appData.updatedAt && appData.updatedAt !== appData.submittedAt) {
          fallbackHistory.push({
            id: 'fallback-2',
            applicationId: appData.id,
            toStatus: appData.status,
            changedAt: appData.updatedAt,
            comments: 'Status updated',
          } as ApplicationStatusHistory);
        }
        setStatusHistory(fallbackHistory.reverse());
      }

    } catch (err: any) {
      console.error('Error loading application details:', err);
      console.error('Error details:', {
        status: err.response?.status,
        message: err.response?.data?.message || err.message,
        url: err.config?.url,
      });
      
      // Only show error if it's a critical failure (main application fetch failed)
      const errorMessage = err.response?.data?.message || err.message;
      const status = err.response?.status;
      
      // Check if it's a server error (500) or network error
      // Only set error state - don't show toast as error is displayed in UI
      if (status === 500 || !err.response) {
        const serverErrorMsg = t('common.errors.serverError', { defaultValue: 'Server error. Please try again later.' });
        setError(serverErrorMsg);
        // Don't show toast - error is displayed in the UI
      } else if (status === 404) {
        const notFoundMsg = t('application.error.notFound', { defaultValue: 'Application not found' });
        setError(notFoundMsg);
        // Don't show toast - error is displayed in the UI
      } else {
        const genericErrorMsg = errorMessage || t('common.errorLoadingData', { defaultValue: 'Error loading data' });
        setError(genericErrorMsg);
        // Don't show toast - error is displayed in the UI
      }
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'success' | 'error' | 'warning' => {
    switch (status) {
      case 'APPROVED':
      case 'COMPLETED':
        return 'success';
      case 'REJECTED':
      case 'WITHDRAWN':
        return 'error';
      case 'UNDER_REVIEW':
      case 'PENDING_DOCS':
        return 'warning';
      case 'SUBMITTED':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED':
      case 'COMPLETED':
        return <CheckCircleIcon />;
      case 'REJECTED':
      case 'WITHDRAWN':
        return <CancelIcon />;
      case 'UNDER_REVIEW':
      case 'PENDING_DOCS':
        return <PendingIcon />;
      case 'SUBMITTED':
        return <ScheduleIcon />;
      default:
        return <AssignmentIcon />;
    }
  };

  const getStatusLabel = (status: string): string => {
    const statusMap: Record<string, string> = {
      SUBMITTED: t('application.status.submitted', { defaultValue: 'Submitted' }),
      UNDER_REVIEW: t('application.status.underReview', { defaultValue: 'Under Review' }),
      PENDING_DOCS: t('application.status.pendingDocs', { defaultValue: 'Pending Documents' }),
      APPROVED: t('application.status.approved', { defaultValue: 'Approved' }),
      REJECTED: t('application.status.rejected', { defaultValue: 'Rejected' }),
      WITHDRAWN: t('application.status.withdrawn', { defaultValue: 'Withdrawn' }),
      COMPLETED: t('application.status.completed', { defaultValue: 'Completed' }),
    };
    return statusMap[status] || status;
  };

  const getServiceTypeLabel = (serviceType: string): string => {
    const serviceTypeMap: Record<string, string> = {
      'Scheme Application': t('application.submit.serviceTypes.schemeApplication', { defaultValue: 'Scheme Application' }),
      'Benefit Claim': t('application.submit.serviceTypes.benefitClaim', { defaultValue: 'Benefit Claim' }),
      'Document Verification': t('application.submit.serviceTypes.documentVerification', { defaultValue: 'Document Verification' }),
      'Status Inquiry': t('application.submit.serviceTypes.statusInquiry', { defaultValue: 'Status Inquiry' }),
      'Complaint/Feedback': t('application.submit.serviceTypes.complaintFeedback', { defaultValue: 'Complaint/Feedback' }),
      'Other': t('application.submit.serviceTypes.other', { defaultValue: 'Other' }),
    };
    return serviceTypeMap[serviceType] || serviceType;
  };

  const getApplicationTypeLabel = (applicationType: string): string => {
    const applicationTypeMap: Record<string, string> = {
      'New': t('application.submit.applicationTypes.new', { defaultValue: 'New' }),
      'Renewal': t('application.submit.applicationTypes.renewal', { defaultValue: 'Renewal' }),
      'Modification': t('application.submit.applicationTypes.modification', { defaultValue: 'Modification' }),
      'Correction': t('application.submit.applicationTypes.correction', { defaultValue: 'Correction' }),
      'Transfer': t('application.submit.applicationTypes.transfer', { defaultValue: 'Transfer' }),
      'Cancellation': t('application.submit.applicationTypes.cancellation', { defaultValue: 'Cancellation' }),
    };
    return applicationTypeMap[applicationType] || applicationType;
  };

  const getPriorityLabel = (priority: string): string => {
    const priorityMap: Record<string, string> = {
      'LOW': t('common.priority.low', { defaultValue: 'Low' }),
      'NORMAL': t('common.priority.normal', { defaultValue: 'Normal' }),
      'HIGH': t('common.priority.high', { defaultValue: 'High' }),
      'URGENT': t('common.priority.urgent', { defaultValue: 'Urgent' }),
    };
    return priorityMap[priority] || priority;
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getProgressPercentage = (status: string): number => {
    const statusOrder = ['SUBMITTED', 'UNDER_REVIEW', 'PENDING_DOCS', 'APPROVED', 'REJECTED', 'COMPLETED', 'WITHDRAWN'];
    const currentIndex = statusOrder.indexOf(status);
    if (currentIndex === -1) return 0;
    return ((currentIndex + 1) / statusOrder.length) * 100;
  };

  const handleAccordionChange = (section: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedSection(isExpanded ? section : false);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  // Debug logging
  console.log('Render check - loading:', loading, 'error:', error, 'application:', application?.applicationNumber);

  // Only show error if we have an error AND no application (don't show error if application loaded successfully)
  if (error && !application) {
    console.log('Showing error state - error:', error, 'application:', application);
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || t('application.error.notFound', { defaultValue: 'Application not found' })}
        </Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/applications')}>
          {t('common.backToApplications', { defaultValue: 'Back to Applications' })}
        </Button>
      </Container>
    );
  }

  // If no application but no error and not loading, show not found
  if (!application && !loading && !error) {
    console.log('Showing not found state');
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning" sx={{ mb: 3 }}>
          {t('application.error.notFound', { defaultValue: 'Application not found' })}
        </Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/applications')}>
          {t('common.backToApplications', { defaultValue: 'Back to Applications' })}
        </Button>
      </Container>
    );
  }

  // Ensure application exists before rendering main content
  if (!application) {
    console.log('Application not loaded yet, returning null');
    return null; // Still loading or error state handled above
  }

  console.log('Rendering main content for application:', application.applicationNumber);

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link to="/dashboard" style={{ textDecoration: 'none', color: 'inherit' }}>
          {t('menu.dashboard', { defaultValue: 'Dashboard' })}
        </Link>
        <Link to="/applications" style={{ textDecoration: 'none', color: 'inherit' }}>
          {t('menu.myApplications', { defaultValue: 'My Applications' })}
        </Link>
        <Typography color="text.primary">
          {application.applicationNumber || `APP-${application.id.slice(0, 8).toUpperCase()}`}
        </Typography>
      </Breadcrumbs>

      {/* Back Button */}
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/applications')} sx={{ mb: 3 }}>
        {t('common.back', { defaultValue: 'Back' })}
      </Button>

      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            {t('application.details.title', { defaultValue: 'Application Details' })}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isConnected && (
              <Chip
                label={t('application.realtime.active', { defaultValue: 'Live Updates' })}
                color="success"
                size="small"
                sx={{ fontSize: '0.7rem' }}
              />
            )}
            <Chip
              icon={getStatusIcon(application.status)}
              label={getStatusLabel(application.status)}
              color={getStatusColor(application.status)}
              size="medium"
            />
          </Box>
        </Box>
        <Typography variant="h6" color="text.secondary">
          {application.applicationNumber || `APP-${application.id.slice(0, 8).toUpperCase()}`}
        </Typography>
      </Box>

      {/* Progress Bar */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="subtitle2" gutterBottom>
          {t('application.progress', { defaultValue: 'Application Progress' })}
        </Typography>
        <LinearProgress
          variant="determinate"
          value={getProgressPercentage(application.status)}
          sx={{ height: 8, borderRadius: 4, mb: 1 }}
        />
        <Typography variant="caption" color="text.secondary">
          {getStatusLabel(application.status)}
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        {/* Left Column - Main Details */}
        <Grid item xs={12} md={8}>
          {/* Application Details */}
          <Accordion expanded={expandedSection === 'details'} onChange={handleAccordionChange('details')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AssignmentIcon />
                <Typography variant="h6">
                  {t('application.details.basicInfo', { defaultValue: 'Basic Information' })}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    {t('application.applicationNumber', { defaultValue: 'Application Number' })}
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {application.applicationNumber || `APP-${application.id.slice(0, 8).toUpperCase()}`}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    {t('application.statusLabel', { defaultValue: 'Status' })}
                  </Typography>
                  <Chip
                    icon={getStatusIcon(application.status)}
                    label={getStatusLabel(application.status)}
                    color={getStatusColor(application.status)}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    {t('application.serviceType', { defaultValue: 'Service Type' })}
                  </Typography>
                  <Typography variant="body1">{getServiceTypeLabel(application.serviceType || '')}</Typography>
                </Grid>
                {application.applicationType && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.applicationType', { defaultValue: 'Application Type' })}
                    </Typography>
                    <Typography variant="body1">{getApplicationTypeLabel(application.applicationType)}</Typography>
                  </Grid>
                )}
                {scheme && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.scheme', { defaultValue: 'Scheme' })}
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <SchemeIcon fontSize="small" />
                      <Link
                        to={`/schemes/${scheme.id}`}
                        style={{ textDecoration: 'none', color: 'inherit' }}
                      >
                        <Typography variant="body1" color="primary">
                          {getSchemeName(scheme, i18n.language)}
                        </Typography>
                      </Link>
                    </Box>
                  </Grid>
                )}
                {application.priority && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.priority', { defaultValue: 'Priority' })}
                    </Typography>
                    <Typography variant="body1">{getPriorityLabel(application.priority)}</Typography>
                  </Grid>
                )}
                <Grid item xs={12} sm={6}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    {t('application.submittedAt', { defaultValue: 'Submitted On' })}
                  </Typography>
                  <Typography variant="body1">{formatDate(application.submittedAt)}</Typography>
                </Grid>
                {application.expectedCompletionDate && (
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.expectedCompletion', { defaultValue: 'Expected Completion' })}
                    </Typography>
                    <Typography variant="body1">{formatDate(application.expectedCompletionDate)}</Typography>
                  </Grid>
                )}
                {application.subject && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.subject', { defaultValue: 'Subject' })}
                    </Typography>
                    <Typography variant="body1">{application.subject}</Typography>
                  </Grid>
                )}
                {application.description && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                      {t('application.description', { defaultValue: 'Description' })}
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {application.description}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </AccordionDetails>
          </Accordion>

          {/* Status History / Timeline */}
          <Accordion
            expanded={expandedSection === 'timeline'}
            onChange={handleAccordionChange('timeline')}
            sx={{ mt: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TimelineIcon />
                <Typography variant="h6">
                  {t('application.timeline.title', { defaultValue: 'Status Timeline' })}
                </Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {statusHistory.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  {t('application.timeline.noHistory', { defaultValue: 'No status history available' })}
                </Typography>
              ) : (
                <Box sx={{ position: 'relative', pl: 3 }}>
                  {statusHistory.map((item, index) => (
                    <Box key={item.id || index} sx={{ position: 'relative', pb: 3 }}>
                      {/* Timeline Line */}
                      {index < statusHistory.length - 1 && (
                        <Box
                          sx={{
                            position: 'absolute',
                            left: 6,
                            top: 24,
                            bottom: -12,
                            width: 2,
                            bgcolor: 'divider',
                          }}
                        />
                      )}
                      {/* Timeline Dot */}
                      <Box
                        sx={{
                          position: 'absolute',
                          left: 0,
                          top: 4,
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: getStatusColor(item.toStatus) === 'success' ? 'success.main' :
                                   getStatusColor(item.toStatus) === 'error' ? 'error.main' :
                                   getStatusColor(item.toStatus) === 'warning' ? 'warning.main' :
                                   'primary.main',
                          border: 2,
                          borderColor: 'background.paper',
                        }}
                      />
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5, flexWrap: 'wrap' }}>
                          {item.fromStatus && (
                            <Chip
                              label={getStatusLabel(item.fromStatus)}
                              size="small"
                              variant="outlined"
                              sx={{ mr: 0.5 }}
                            />
                          )}
                          <Typography variant="caption" color="text.secondary" sx={{ mr: 0.5 }}>
                            →
                          </Typography>
                          <Chip
                            icon={getStatusIcon(item.toStatus)}
                            label={getStatusLabel(item.toStatus)}
                            color={getStatusColor(item.toStatus)}
                            size="small"
                          />
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                            {formatDate(item.changedAt)}
                          </Typography>
                        </Box>
                        {item.stage && (
                          <Typography variant="caption" color="primary" sx={{ display: 'block', mb: 0.5 }}>
                            {item.stage}
                          </Typography>
                        )}
                        {item.comments && (
                          <Typography variant="body2" color="text.secondary">
                            {item.comments}
                          </Typography>
                        )}
                        {item.changedByType && (
                          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                            {t('application.timeline.changedBy', {
                              defaultValue: 'Changed by',
                            })}{' '}
                            {item.changedByType}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}
            </AccordionDetails>
          </Accordion>

          {/* Application Data */}
          {application.applicationData && Object.keys(application.applicationData).length > 0 && (
            <Accordion
              expanded={expandedSection === 'data'}
              onChange={handleAccordionChange('data')}
              sx={{ mt: 2 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <DescriptionIcon />
                  <Typography variant="h6">
                    {t('application.data.title', { defaultValue: 'Application Data' })}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                  <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                    {JSON.stringify(application.applicationData, null, 2)}
                  </pre>
                </Paper>
              </AccordionDetails>
            </Accordion>
          )}
        </Grid>

        {/* Right Column - Actions & Documents */}
        <Grid item xs={12} md={4}>
          {/* Quick Actions */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('application.actions.title', { defaultValue: 'Quick Actions' })}
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<PaymentIcon />}
                  component={Link}
                  to={`/payments?applicationId=${application.id}`}
                >
                  {t('application.makePayment', { defaultValue: 'Make Payment' })}
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<DescriptionIcon />}
                  component={Link}
                  to={`/documents?applicationId=${application.id}`}
                >
                  {t('application.viewDocuments', { defaultValue: 'View Documents' })}
                </Button>
                <Button
                  variant="outlined"
                  fullWidth
                  startIcon={<DownloadIcon />}
                  onClick={async () => {
                    try {
                      // Get payment for this application
                      const payments = await paymentService.getPaymentsByApplication(application.id);
                      if (payments && payments.length > 0) {
                        const latestPayment = payments.find(p => p.status === 'SUCCESS' || p.status === 'COMPLETED') || payments[0];
                        const { generatePaymentReceiptPdf } = await import('@/utils/receiptGenerator');
                        generatePaymentReceiptPdf(latestPayment, application, t);
                        showSuccess(t('application.download.success', { defaultValue: 'Receipt downloaded successfully' }));
                      } else {
                        showInfo(t('application.download.noPayment', { defaultValue: 'No payment found for this application' }));
                      }
                    } catch (error) {
                      console.error('Error downloading receipt:', error);
                      showError(t('application.download.error', { defaultValue: 'Failed to download receipt' }));
                    }
                  }}
                >
                  {t('application.downloadReceipt', { defaultValue: 'Download Receipt' })}
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Documents */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                {t('application.documents.title', { defaultValue: 'Attached Documents' })}
              </Typography>
              {documents.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {t('application.documents.noDocuments', { defaultValue: 'No documents attached' })}
                </Typography>
              ) : (
                <List dense sx={{ mb: 2 }}>
                  {documents.map((doc) => (
                    <ListItem key={doc.id} disablePadding>
                      <ListItemIcon>
                        <DescriptionIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={doc.documentName || doc.fileName || 'Document'}
                        secondary={
                          <Chip
                            label={doc.verificationStatus || 'PENDING'}
                            size="small"
                            color={doc.verificationStatus === 'VERIFIED' ? 'success' : 'default'}
                          />
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              {user?.id && /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(user.id) && (
                <Box sx={{ mb: 2 }}>
                  <DocumentUpload
                    citizenId={user.id}
                    applicationId={application.id}
                    onUploadSuccess={async () => {
                      if (id) {
                        const appDocs = await documentService.getDocumentsByApplication(id);
                        setDocuments(appDocs);
                      }
                    }}
                  />
                </Box>
              )}
              <Button
                size="small"
                variant="text"
                fullWidth
                component={Link}
                to={`/documents?applicationId=${application.id}`}
              >
                {t('application.documents.viewAll', { defaultValue: 'View All Documents' })}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

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

export default ApplicationDetailPage;

