import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getUserName } from '@/utils/localization';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  CardGiftcard as BenefitsIcon,
  Folder as DocumentsIcon,
  LocalOffer as SchemesIcon,
  Notifications as NotificationsIcon,
  TrendingUp as TrendingUpIcon,
  Receipt as ReceiptIcon,
} from '@mui/icons-material';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { fetchCurrentUser } from '@/store/slices/auth.slice';
import { applicationService, notificationService, documentService, schemeService } from '@/services';
import { ServiceApplication, Notification, Document, Scheme } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { Link } from 'react-router-dom';

const DashboardPage: React.FC = () => {
  const { t, i18n } = useTranslation(['common', 'dashboard']);
  const dispatch = useAppDispatch();
  const authState = useAppSelector((state) => state.auth);
  const { user, isAuthenticated } = authState;
  const { dialog, showError, close } = useMessageDialog();

  // Debug: Log current language and available translations
  React.useEffect(() => {
    console.log('Current language:', i18n.language);
    console.log('Dashboard translations available:', i18n.hasResourceBundle(i18n.language, 'dashboard'));
    console.log('Dashboard subtitle translation:', t('subtitle', { ns: 'dashboard' }));
  }, [i18n, t]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Statistics
  const [applicationsCount, setApplicationsCount] = useState(0);
  const [documentsCount, setDocumentsCount] = useState(0);
  const [notificationsCount, setNotificationsCount] = useState(0);
  const [unreadNotificationsCount, setUnreadNotificationsCount] = useState(0);
  const [schemesCount, setSchemesCount] = useState(0);

  // Recent items
  const [recentApplications, setRecentApplications] = useState<ServiceApplication[]>([]);
  const [recentNotifications, setRecentNotifications] = useState<Notification[]>([]);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }

    // If we don't have user data yet, try to fetch it
    if (!user?.id) {
      dispatch(fetchCurrentUser())
        .unwrap()
        .then((fetchedUser) => {
          // User fetched successfully, load dashboard data
          if (fetchedUser?.id) {
            loadDashboardData();
          } else {
            setLoading(false);
          }
        })
        .catch((error) => {
          // User fetch failed (404 = user not found, or other error)
          // Continue with dashboard anyway (will show 0 counts)
          console.log('User profile not found or error, continuing with dashboard:', error);
          setLoading(false);
        });
      return;
    }

    // We have user ID, load dashboard data
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, user?.id, dispatch, authState.user?.id]);

  const loadDashboardData = async () => {
    // Get latest user from authState (may have been updated by fetchCurrentUser)
    const currentUser = authState.user || user;
    const userId = currentUser?.id;
    
    if (!userId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Validate userId is a valid UUID (not mock-id)
      const isValidUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(userId);
      
      if (!isValidUUID) {
        // User ID is not valid (e.g., mock-id), skip API calls
        console.log('Invalid user ID, skipping API calls');
        setLoading(false);
        return;
      }

      // Load data in parallel
      const [applicationsData, notificationsData, documentsData, schemesData, unreadCount] = await Promise.allSettled([
        applicationService.getApplicationsByCitizen(userId, 0, 5), // Get first 5 applications
        notificationService.getNotificationsByCitizen(userId, 0, 5), // Get first 5 notifications
        documentService.getDocumentsByCitizen(userId), // Get documents
        schemeService.getSchemes(0, 100, 'ACTIVE'), // Get active schemes
        notificationService.getUnreadCount(userId), // Get unread count
      ]);

      // Handle applications
      if (applicationsData.status === 'fulfilled') {
        setApplicationsCount(applicationsData.value.totalElements);
        setRecentApplications(applicationsData.value.content.slice(0, 5));
      }

      // Handle notifications
      if (notificationsData.status === 'fulfilled') {
        setNotificationsCount(notificationsData.value.totalElements);
        setRecentNotifications(notificationsData.value.content.slice(0, 5));
      }

      if (unreadCount.status === 'fulfilled') {
        setUnreadNotificationsCount(unreadCount.value);
      }

      // Handle documents
      if (documentsData.status === 'fulfilled') {
        setDocumentsCount(documentsData.value.length);
      }

      // Handle schemes
      if (schemesData.status === 'fulfilled') {
        setSchemesCount(schemesData.value.totalElements);
      }
    } catch (err: any) {
      console.error('Error loading dashboard data:', err);
      const errorMessage = err.message || t('dashboard.errors.loadFailed', { defaultValue: 'Failed to load some dashboard data' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    const upperStatus = status.toUpperCase();
    if (upperStatus.includes('APPROVED') || upperStatus.includes('COMPLETED')) return 'success';
    if (upperStatus.includes('REJECTED') || upperStatus.includes('FAILED')) return 'error';
    if (upperStatus.includes('PENDING')) return 'warning';
    if (upperStatus.includes('IN_PROGRESS')) return 'info';
    return 'default';
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {t('loadingDashboard', { ns: 'dashboard', defaultValue: 'Loading dashboard...' })}
          </Typography>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Welcome Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('common.welcome')}, {user ? getUserName(user, i18n.language) : (user?.mobileNumber || 'User')}!
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('subtitle', { ns: 'dashboard', defaultValue: 'Here\'s an overview of your account' })}
        </Typography>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" color="primary">
                    {applicationsCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('menu.myApplications')}
                  </Typography>
                </Box>
                <AssignmentIcon sx={{ fontSize: 40, color: 'primary.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" color="success.main">
                    {schemesCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('menu.schemes')}
                  </Typography>
                </Box>
                <SchemesIcon sx={{ fontSize: 40, color: 'success.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" color="info.main">
                    {documentsCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('menu.documents')}
                  </Typography>
                </Box>
                <DocumentsIcon sx={{ fontSize: 40, color: 'info.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h4" color="warning.main">
                    {notificationsCount}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('menu.notifications', { defaultValue: 'Notifications' })}
                    {unreadNotificationsCount > 0 && (
                      <Chip
                        label={unreadNotificationsCount}
                        size="small"
                        color="error"
                        sx={{ ml: 1, height: 20, fontSize: '0.7rem' }}
                      />
                    )}
                  </Typography>
                </Box>
                <NotificationsIcon sx={{ fontSize: 40, color: 'warning.main', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Applications */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {t('recentApplications', { ns: 'dashboard', defaultValue: 'Recent Applications' })}
              </Typography>
              <Button component={Link} to="/applications" size="small" variant="outlined">
                {t('common.viewAll', { defaultValue: 'View All' })}
              </Button>
            </Box>

            {recentApplications.length > 0 ? (
              <List>
                {recentApplications.map((app) => (
                  <ListItem
                    key={app.id}
                    component={Link}
                    to={`/applications/${app.id}`}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      '&:hover': { bgcolor: 'action.hover' },
                    }}
                  >
                    <ListItemIcon>
                      <AssignmentIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={app.applicationNumber || `Application #${app.id.substring(0, 8)}`}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Chip
                            label={app.status}
                            size="small"
                            color={getStatusColor(app.status)}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {app.serviceType}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <AssignmentIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  {t('noApplications', { ns: 'dashboard', defaultValue: 'No applications yet' })}
                </Typography>
                <Button component={Link} to="/schemes" variant="contained" sx={{ mt: 2 }}>
                  {t('browseSchemes', { ns: 'dashboard', defaultValue: 'Browse Schemes' })}
                </Button>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Recent Notifications */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                {t('recentNotifications', { ns: 'dashboard', defaultValue: 'Recent Notifications' })}
              </Typography>
              <Button component={Link} to="/notifications" size="small" variant="outlined">
                {t('common.viewAll', { defaultValue: 'View All' })}
              </Button>
            </Box>

            {recentNotifications.length > 0 ? (
              <List>
                {recentNotifications.map((notification) => (
                  <ListItem
                    key={notification.id}
                    sx={{
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1,
                      mb: 1,
                      bgcolor: notification.isRead ? 'transparent' : 'action.hover',
                    }}
                  >
                    <ListItemIcon>
                      <NotificationsIcon color={notification.isRead ? 'disabled' : 'primary'} />
                    </ListItemIcon>
                    <ListItemText
                      primary={notification.subject || notification.message.substring(0, 50)}
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {notification.createdAt
                            ? new Date(notification.createdAt).toLocaleDateString()
                            : 'Recent'}
                        </Typography>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            ) : (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <NotificationsIcon sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  {t('noNotifications', { ns: 'dashboard', defaultValue: 'No notifications' })}
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Message Dialog */}
      <MessageDialog
        open={dialog.open}
        onClose={close}
        type={dialog.type}
        message={dialog.message}
        title={dialog.title}
      />
    </Container>
  );
};

export default DashboardPage;
