import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Chip,
  Button,
  CircularProgress,
  Alert,
  Pagination,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsActive as NotificationsActiveIcon,
  CheckCircle as CheckCircleIcon,
  MarkEmailRead as MarkEmailReadIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  CheckCircleOutline as CheckCircleOutlineIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { notificationService } from '@/services/notification.service';
import { Notification, PagedResponse } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { isValidUUID } from '@/utils/uuidValidator';
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
      id={`notifications-tabpanel-${index}`}
      aria-labelledby={`notifications-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const NotificationsPage: React.FC = () => {
  const { t } = useTranslation();
  const { user, isAuthenticated, profileNotFound } = useAppSelector((state) => state.auth);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0); // 0: All, 1: Unread
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadNotifications, setUnreadNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);
  const pageSize = 20;

  const loadNotifications = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      setError(t('notifications.invalidUserId', { defaultValue: 'Invalid user ID. Cannot load notifications.' }));
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response: PagedResponse<Notification> = await notificationService.getNotificationsByCitizen(
        user.id,
        page,
        pageSize
      );
      setNotifications(response.content || []);
      setTotalPages(response.totalPages || 0);
      setTotalElements(response.totalElements || 0);
    } catch (err: any) {
      console.error('Failed to load notifications:', err);
      const errorMessage = err.response?.data?.message || t('notifications.loadFailed', { defaultValue: 'Failed to load notifications' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadNotifications = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      return;
    }

    try {
      const unread = await notificationService.getUnreadNotifications(user.id);
      setUnreadNotifications(unread);
    } catch (err: any) {
      console.error('Failed to load unread notifications:', err);
    }
  };

  const loadUnreadCount = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      return;
    }

    try {
      const count = await notificationService.getUnreadCount(user.id);
      setUnreadCount(count);
    } catch (err: any) {
      console.error('Failed to load unread count:', err);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      setError(t('notifications.notAuthenticated', { defaultValue: 'You must be logged in to view notifications.' }));
      return;
    }

    if (profileNotFound || !user?.id || !isValidUUID(user.id)) {
      setLoading(false);
      setError(t('notifications.profileNeeded', { defaultValue: 'Please complete your profile before viewing notifications.' }));
      return;
    }

    loadNotifications();
    loadUnreadNotifications();
    loadUnreadCount();
  }, [user?.id, isAuthenticated, profileNotFound, page]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    setPage(0); // Reset to first page when switching tabs
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    setPage(value - 1); // MUI Pagination is 1-based, API is 0-based
  };

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await notificationService.markAsRead(notificationId);
      showSuccess(t('notifications.markedAsRead', { defaultValue: 'Notification marked as read' }));
      // Refresh notifications
      loadNotifications();
      loadUnreadNotifications();
      loadUnreadCount();
    } catch (err: any) {
      console.error('Failed to mark notification as read:', err);
      showError(err.response?.data?.message || t('notifications.markAsReadFailed', { defaultValue: 'Failed to mark notification as read' }));
    }
  };

  const handleMarkAllAsRead = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      return;
    }

    try {
      await notificationService.markAllAsRead(user.id);
      showSuccess(t('notifications.allMarkedAsRead', { defaultValue: 'All notifications marked as read' }));
      // Refresh notifications
      loadNotifications();
      loadUnreadNotifications();
      loadUnreadCount();
    } catch (err: any) {
      console.error('Failed to mark all notifications as read:', err);
      showError(err.response?.data?.message || t('notifications.markAllAsReadFailed', { defaultValue: 'Failed to mark all notifications as read' }));
    }
  };

  const getNotificationIcon = (type: string, isRead: boolean) => {
    const iconProps = { color: isRead ? 'disabled' : 'primary' as const };
    switch (type?.toUpperCase()) {
      case 'INFO':
        return <InfoIcon {...iconProps} />;
      case 'WARNING':
        return <WarningIcon {...iconProps} />;
      case 'ERROR':
        return <ErrorIcon {...iconProps} />;
      case 'SUCCESS':
        return <CheckCircleOutlineIcon {...iconProps} />;
      default:
        return isRead ? <NotificationsIcon {...iconProps} /> : <NotificationsActiveIcon {...iconProps} />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'INFO':
        return 'info';
      case 'WARNING':
        return 'warning';
      case 'ERROR':
        return 'error';
      case 'SUCCESS':
        return 'success';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t('notifications.justNow', { defaultValue: 'Just now' });
    if (diffMins < 60) return t('notifications.minutesAgo', { defaultValue: '{{count}} minutes ago', count: diffMins });
    if (diffHours < 24) return t('notifications.hoursAgo', { defaultValue: '{{count}} hours ago', count: diffHours });
    if (diffDays < 7) return t('notifications.daysAgo', { defaultValue: '{{count}} days ago', count: diffDays });
    return date.toLocaleDateString();
  };

  const renderNotificationList = (notificationList: Notification[]) => {
    if (notificationList.length === 0) {
      return (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <NotificationsIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            {tabValue === 0
              ? t('notifications.noNotifications', { defaultValue: 'No notifications found' })
              : t('notifications.noUnreadNotifications', { defaultValue: 'No unread notifications' })}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {tabValue === 0
              ? t('notifications.noNotificationsDescription', { defaultValue: 'You will see notifications here when they arrive.' })
              : t('notifications.noUnreadNotificationsDescription', { defaultValue: 'All caught up! No unread notifications.' })}
          </Typography>
        </Box>
      );
    }

    return (
      <List>
        {notificationList.map((notification, index) => (
          <React.Fragment key={notification.id}>
            <ListItem
              sx={{
                bgcolor: notification.isRead ? 'transparent' : 'action.hover',
                borderLeft: notification.isRead ? 'none' : '4px solid',
                borderColor: notification.isRead ? 'transparent' : 'primary.main',
                '&:hover': {
                  bgcolor: 'action.selected',
                },
              }}
              secondaryAction={
                !notification.isRead ? (
                  <Tooltip title={t('notifications.markAsRead', { defaultValue: 'Mark as read' })}>
                    <IconButton
                      edge="end"
                      onClick={() => handleMarkAsRead(notification.id)}
                      size="small"
                    >
                      <MarkEmailReadIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                ) : null
              }
            >
              <ListItemIcon>{getNotificationIcon(notification.type, notification.isRead)}</ListItemIcon>
              <ListItemButton
                component={notification.applicationId ? Link : 'div'}
                to={notification.applicationId ? `/applications/${notification.applicationId}` : undefined}
                onClick={() => {
                  if (!notification.isRead) {
                    handleMarkAsRead(notification.id);
                  }
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle1" component="span" fontWeight={notification.isRead ? 400 : 600}>
                        {notification.subject || notification.message.substring(0, 60)}
                      </Typography>
                      <Chip
                        label={notification.type}
                        size="small"
                        color={getNotificationColor(notification.type) as any}
                        sx={{ height: 20, fontSize: '0.7rem' }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary">
                        {notification.message}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                        {formatDate(notification.createdAt || notification.sentAt)}
                        {notification.channel && ` • ${t(`notifications.channel.${notification.channel.toLowerCase()}`, { defaultValue: notification.channel })}`}
                      </Typography>
                    </Box>
                  }
                />
              </ListItemButton>
            </ListItem>
            {index < notificationList.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    );
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error">{error}</Alert>
        {!isAuthenticated && (
          <Button variant="contained" sx={{ mt: 2 }} component={Link} to="/login">
            {t('common.login', { defaultValue: 'Login' })}
          </Button>
        )}
        {(profileNotFound || !user?.id) && isAuthenticated && (
          <Button variant="contained" sx={{ mt: 2 }} component={Link} to="/profile">
            {t('profile.completeProfile', { defaultValue: 'Complete Profile' })}
          </Button>
        )}
      </Container>
    );
  }

  const displayNotifications = tabValue === 0 ? notifications : unreadNotifications;

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('notifications.title', { defaultValue: 'Notifications' })}
        </Typography>
        {unreadCount > 0 && (
          <Button
            variant="outlined"
            startIcon={<CheckCircleIcon />}
            onClick={handleMarkAllAsRead}
            disabled={loading}
          >
            {t('notifications.markAllAsRead', { defaultValue: 'Mark All as Read' })}
          </Button>
        )}
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('notifications.all', { defaultValue: 'All' })}
                {totalElements > 0 && (
                  <Chip label={totalElements} size="small" sx={{ height: 20 }} />
                )}
              </Box>
            }
          />
          <Tab
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('notifications.unread', { defaultValue: 'Unread' })}
                {unreadCount > 0 && (
                  <Chip label={unreadCount} size="small" color="primary" sx={{ height: 20 }} />
                )}
              </Box>
            }
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {renderNotificationList(notifications)}
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
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {renderNotificationList(unreadNotifications)}
        </TabPanel>
      </Paper>

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

