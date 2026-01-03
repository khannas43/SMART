import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Pagination,
  InputAdornment,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Pending as PendingIcon,
  Schedule as ScheduleIcon,
  Description as DescriptionIcon,
  Download as DownloadIcon,
  Visibility as VisibilityIcon,
  FilterList as FilterListIcon,
  Search as SearchIcon,
  LocalOffer as SchemeIcon,
  CalendarToday as CalendarIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@/store/hooks';
import { applicationService, schemeService } from '@/services';
import { ServiceApplication, Scheme } from '@/types/api';
import { useWebSocket } from '@/hooks/useWebSocket';
import { getSchemeName } from '@/utils/localization';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

// Status definitions
const ACTIVE_STATUSES = ['SUBMITTED', 'UNDER_REVIEW', 'PENDING_DOCS', 'APPROVED', 'REJECTED'];
const PAST_STATUSES = ['APPROVED', 'REJECTED', 'WITHDRAWN', 'COMPLETED'];
// Get unique statuses for dropdown (remove duplicates)
const ALL_STATUSES = Array.from(new Set([...ACTIVE_STATUSES, ...PAST_STATUSES]));

const ApplicationsHubPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Applications data
  const [activeApplications, setActiveApplications] = useState<ServiceApplication[]>([]);
  const [pastApplications, setPastApplications] = useState<ServiceApplication[]>([]);
  const [allApplications, setAllApplications] = useState<ServiceApplication[]>([]);

  // Schemes for filter
  const [schemes, setSchemes] = useState<Scheme[]>([]);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedScheme, setSelectedScheme] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: '',
    end: '',
  });

  // Pagination
  const [page, setPage] = useState(0);
  const [size] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);

  // Expanded accordions
  const [expandedApp, setExpandedApp] = useState<string | false>(false);

  // WebSocket for real-time updates - subscribe to all user's applications
  const { isConnected } = useWebSocket({
    topics: user?.id ? [`/queue/citizen/${user.id}/applications`] : [],
    onMessage: (message) => {
      // Handle real-time status update
      showSuccess(message.message || t('application.status.updated', { defaultValue: 'Application status updated' }));
      
      // Reload applications to reflect updated status
      loadData();
    },
    onError: (error) => {
      console.error('WebSocket error:', error);
    },
    autoConnect: !!user?.id,
  });

  useEffect(() => {
    if (!user?.id) {
      setLoading(false);
      return;
    }

    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, page]);

  useEffect(() => {
    // Filter applications when filters change
    filterApplications();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, selectedScheme, selectedStatus, dateRange, allApplications]);

  const loadData = async () => {
    if (!user?.id) return;

    setLoading(true);
    setError(null);

    try {
      // Load schemes for filter dropdown
      try {
        const schemesData = await schemeService.getSchemes(0, 100, 'ACTIVE');
        if (schemesData && schemesData.content && Array.isArray(schemesData.content)) {
          setSchemes(schemesData.content);
          console.log('Schemes loaded:', schemesData.content.length);
        } else {
          console.warn('No schemes data received or invalid format:', schemesData);
          setSchemes([]);
        }
      } catch (schemeErr: any) {
        console.error('Error loading schemes:', schemeErr);
        setSchemes([]);
      }

      // Load applications
      const applicationsData = await applicationService.getApplicationsByCitizen(
        user.id,
        page,
        size
      );

      setAllApplications(applicationsData.content);
      setTotalPages(applicationsData.totalPages);
      setTotalElements(applicationsData.totalElements);

      // Separate into active and past
      const active = applicationsData.content.filter((app) =>
        ACTIVE_STATUSES.includes(app.status)
      );
      const past = applicationsData.content.filter((app) => PAST_STATUSES.includes(app.status));

      setActiveApplications(active);
      setPastApplications(past);
    } catch (err: any) {
      console.error('Error loading applications:', err);
      const errorMessage = err.message || t('common.errorLoadingData', { defaultValue: 'Error loading data' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const filterApplications = () => {
    let filtered = [...allApplications];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (app) =>
          app.applicationNumber?.toLowerCase().includes(query) ||
          app.subject?.toLowerCase().includes(query) ||
          app.description?.toLowerCase().includes(query) ||
          app.serviceType?.toLowerCase().includes(query)
      );
    }

    // Scheme filter
    if (selectedScheme) {
      filtered = filtered.filter((app) => app.schemeId === selectedScheme);
    }

    // Status filter
    if (selectedStatus) {
      filtered = filtered.filter((app) => app.status === selectedStatus);
    }

    // Date range filter
    if (dateRange.start) {
      filtered = filtered.filter((app) => {
        if (!app.submittedAt) return false;
        return new Date(app.submittedAt) >= new Date(dateRange.start);
      });
    }
    if (dateRange.end) {
      filtered = filtered.filter((app) => {
        if (!app.submittedAt) return false;
        return new Date(app.submittedAt) <= new Date(dateRange.end);
      });
    }

    // Separate into active and past
    const active = filtered.filter((app) => ACTIVE_STATUSES.includes(app.status));
    const past = filtered.filter((app) => PAST_STATUSES.includes(app.status));

    setActiveApplications(active);
    setPastApplications(past);
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

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleAccordionChange = (appId: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedApp(isExpanded ? appId : false);
  };

  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value - 1);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSelectedScheme('');
    setSelectedStatus('');
    setDateRange({ start: '', end: '' });
  };

  if (loading && allApplications.length === 0) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, flexWrap: 'wrap', gap: 2 }}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            {t('applications.title', { defaultValue: 'My Applications' })}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {isConnected && (
              <Chip
                label={t('application.realtime.active', { defaultValue: 'Live Updates Active' })}
                color="success"
                size="small"
                icon={<ScheduleIcon />}
              />
            )}
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => navigate('/applications/submit')}
            >
              {t('applications.newApplication', { defaultValue: 'New Application' })}
            </Button>
          </Box>
        </Box>
        <Typography variant="body1" color="text.secondary">
          {t('applications.subtitle', {
            defaultValue: 'Track and manage all your service applications',
          })}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <FilterListIcon sx={{ mr: 1 }} />
          <Typography variant="h6">
            {t('common.filters', { defaultValue: 'Filters' })}
          </Typography>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label={t('common.search', { defaultValue: 'Search' })}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>{t('application.scheme', { defaultValue: 'Scheme' })}</InputLabel>
              <Select
                value={selectedScheme}
                label={t('application.scheme', { defaultValue: 'Scheme' })}
                onChange={(e) => setSelectedScheme(e.target.value)}
              >
                <MenuItem value="">{t('common.all', { defaultValue: 'All' })}</MenuItem>
                {schemes.map((scheme) => (
                  <MenuItem key={scheme.id} value={scheme.id}>
                    {getSchemeName(scheme, i18n.language)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>{t('application.statusLabel', { defaultValue: 'Status' })}</InputLabel>
              <Select
                value={selectedStatus}
                label={t('application.statusLabel', { defaultValue: 'Status' })}
                onChange={(e) => setSelectedStatus(e.target.value)}
                renderValue={(value) => {
                  if (!value) return t('common.all', { defaultValue: 'All' });
                  return getStatusLabel(value);
                }}
              >
                <MenuItem value="">{t('common.all', { defaultValue: 'All' })}</MenuItem>
                {ALL_STATUSES.map((status) => (
                  <MenuItem key={status} value={status}>
                    {getStatusLabel(status)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label={t('application.dateFrom', { defaultValue: 'From Date' })}
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              type="date"
              label={t('application.dateTo', { defaultValue: 'To Date' })}
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          <Grid item xs={12}>
            <Button variant="outlined" onClick={clearFilters} size="small">
              {t('common.clearFilters', { defaultValue: 'Clear Filters' })}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Summary Stats */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="primary">
              {activeApplications.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('applications.active', { defaultValue: 'Active Applications' })}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="text.secondary">
              {pastApplications.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('applications.past', { defaultValue: 'Past Applications' })}
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h4" color="text.secondary">
              {totalElements}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {t('applications.total', { defaultValue: 'Total Applications' })}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Active Applications Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
          <AssignmentIcon sx={{ mr: 1, color: 'primary.main' }} />
          {t('applications.active', { defaultValue: 'Active Applications' })}
          <Chip
            label={activeApplications.length}
            size="small"
            color="primary"
            sx={{ ml: 2 }}
          />
        </Typography>

        {activeApplications.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              {t('applications.noActive', {
                defaultValue: 'No active applications found',
              })}
            </Typography>
          </Paper>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {activeApplications.map((app) => (
              <Accordion
                key={app.id}
                expanded={expandedApp === app.id}
                onChange={handleAccordionChange(app.id)}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                    <Chip
                      icon={getStatusIcon(app.status)}
                      label={getStatusLabel(app.status)}
                      color={getStatusColor(app.status)}
                      size="small"
                    />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {app.applicationNumber || `APP-${app.id.slice(0, 8).toUpperCase()}`}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {app.subject || app.serviceType}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(app.submittedAt)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <List dense>
                        <ListItem>
                          <ListItemIcon>
                            <AssignmentIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.applicationNumber', {
                              defaultValue: 'Application Number',
                            })}
                            secondary={app.applicationNumber || `APP-${app.id.slice(0, 8).toUpperCase()}`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <SchemeIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.serviceType', { defaultValue: 'Service Type' })}
                            secondary={app.serviceType}
                          />
                        </ListItem>
                        {app.schemeId && (
                          <ListItem>
                            <ListItemIcon>
                              <SchemeIcon />
                            </ListItemIcon>
                            <ListItemText
                              primary={t('application.scheme', { defaultValue: 'Scheme' })}
                              secondary={
                                (() => {
                                  const scheme = schemes.find((s) => s.id === app.schemeId);
                                  return scheme ? getSchemeName(scheme, i18n.language) : app.schemeId;
                                })()
                              }
                            />
                          </ListItem>
                        )}
                        <ListItem>
                          <ListItemIcon>
                            <CalendarIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.submittedAt', { defaultValue: 'Submitted On' })}
                            secondary={formatDate(app.submittedAt)}
                          />
                        </ListItem>
                        {app.expectedCompletionDate && (
                          <ListItem>
                            <ListItemIcon>
                              <ScheduleIcon />
                            </ListItemIcon>
                            <ListItemText
                              primary={t('application.expectedCompletion', {
                                defaultValue: 'Expected Completion',
                              })}
                              secondary={formatDate(app.expectedCompletionDate)}
                            />
                          </ListItem>
                        )}
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      {app.description && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            {t('application.description', { defaultValue: 'Description' })}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {app.description}
                          </Typography>
                        </Box>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<VisibilityIcon />}
                          onClick={() => navigate(`/applications/${app.id}`)}
                        >
                          {t('common.viewDetails', { defaultValue: 'View Details' })}
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<DescriptionIcon />}
                          component={Link}
                          to={`/documents?applicationId=${app.id}`}
                        >
                          {t('application.documentsLabel', { defaultValue: 'Documents' })}
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Box>

      <Divider sx={{ my: 4 }} />

      {/* Past Applications Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
          <CheckCircleIcon sx={{ mr: 1, color: 'text.secondary' }} />
          {t('applications.past', { defaultValue: 'Past Applications' })}
          <Chip
            label={pastApplications.length}
            size="small"
            sx={{ ml: 2 }}
          />
        </Typography>

        {pastApplications.length === 0 ? (
          <Paper sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="body1" color="text.secondary">
              {t('applications.noPast', {
                defaultValue: 'No past applications found',
              })}
            </Typography>
          </Paper>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {pastApplications.map((app) => (
              <Accordion
                key={app.id}
                expanded={expandedApp === app.id}
                onChange={handleAccordionChange(app.id)}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                    <Chip
                      icon={getStatusIcon(app.status)}
                      label={getStatusLabel(app.status)}
                      color={getStatusColor(app.status)}
                      size="small"
                    />
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {app.applicationNumber || `APP-${app.id.slice(0, 8).toUpperCase()}`}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {app.subject || app.serviceType}
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(app.submittedAt)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <List dense>
                        <ListItem>
                          <ListItemIcon>
                            <AssignmentIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.applicationNumber', {
                              defaultValue: 'Application Number',
                            })}
                            secondary={app.applicationNumber || `APP-${app.id.slice(0, 8).toUpperCase()}`}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemIcon>
                            <SchemeIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.serviceType', { defaultValue: 'Service Type' })}
                            secondary={app.serviceType}
                          />
                        </ListItem>
                        {app.schemeId && (
                          <ListItem>
                            <ListItemIcon>
                              <SchemeIcon />
                            </ListItemIcon>
                            <ListItemText
                              primary={t('application.scheme', { defaultValue: 'Scheme' })}
                              secondary={
                                (() => {
                                  const scheme = schemes.find((s) => s.id === app.schemeId);
                                  return scheme ? getSchemeName(scheme, i18n.language) : app.schemeId;
                                })()
                              }
                            />
                          </ListItem>
                        )}
                        <ListItem>
                          <ListItemIcon>
                            <CalendarIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={t('application.submittedAt', { defaultValue: 'Submitted On' })}
                            secondary={formatDate(app.submittedAt)}
                          />
                        </ListItem>
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      {app.description && (
                        <Box sx={{ mb: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            {t('application.description', { defaultValue: 'Description' })}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {app.description}
                          </Typography>
                        </Box>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<VisibilityIcon />}
                          onClick={() => navigate(`/applications/${app.id}`)}
                        >
                          {t('common.viewDetails', { defaultValue: 'View Details' })}
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          startIcon={<DownloadIcon />}
                          component={Link}
                          to={`/documents?applicationId=${app.id}`}
                        >
                          {t('application.downloadReceipt', { defaultValue: 'Download Receipt' })}
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
          </Box>
        )}
      </Box>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <Pagination
            count={totalPages}
            page={page + 1}
            onChange={handlePageChange}
            color="primary"
            size="large"
          />
        </Box>
      )}

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

export default ApplicationsHubPage;

