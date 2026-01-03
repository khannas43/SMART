import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Grid,
  Card,
  CardContent,
  FormGroup,
  FormControlLabel,
  Switch,
  TextField,
  Button,
  Divider,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Checkbox,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Block as OptOutIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector, useAppDispatch } from '@/store/hooks';
import { logout } from '@/store/slices/auth.slice';
import { useNavigate, useLocation } from 'react-router-dom';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { isValidUUID } from '@/utils/uuidValidator';
import { citizenService } from '@/services/citizen.service';
import { schemeService } from '@/services/scheme.service';
import { Scheme } from '@/types/api';
import { getSchemeName } from '@/utils/localization';
import { translateCategory, translateDepartment } from '@/utils/categoryTranslator';

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
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface NotificationPreference {
  type: string;
  email: boolean;
  sms: boolean;
  push: boolean;
  inApp: boolean;
}

interface QuietHours {
  enabled: boolean;
  startTime: string;
  endTime: string;
}

export const SettingsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, showInfo, close } = useMessageDialog();

  // Helper function to get translated notification type
  const getNotificationTypeLabel = (type: string): string => {
    // Map English notification types to translation keys
    const typeMap: Record<string, string> = {
      'Application Status Updates': 'settings.notifications.types.applicationStatusUpdates',
      'Payment Notifications': 'settings.notifications.types.paymentNotifications',
      'Document Verification': 'settings.notifications.types.documentVerification',
      'Scheme Announcements': 'settings.notifications.types.schemeAnnouncements',
      'System Updates': 'settings.notifications.types.systemUpdates',
    };
    
    const translationKey = typeMap[type] || `settings.notifications.types.${type.toLowerCase().replace(/\s+/g, '')}`;
    return t(translationKey, { defaultValue: type });
  };

  // Determine initial tab based on URL path
  const getInitialTab = () => {
    if (location.pathname.includes('/notifications')) return 0;
    if (location.pathname.includes('/opt-out')) return 1;
    return 0; // Default to notifications
  };

  const [tabValue, setTabValue] = useState(getInitialTab()); // 0: Notifications, 1: Opt-Out
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [optOutSchemes, setOptOutSchemes] = useState<string[]>([]);

  const [notificationPreferences, setNotificationPreferences] = useState<NotificationPreference[]>([
    { type: 'Application Status Updates', email: true, sms: true, push: true, inApp: true },
    { type: 'Payment Notifications', email: true, sms: false, push: true, inApp: true },
    { type: 'Document Verification', email: true, sms: true, push: false, inApp: true },
    { type: 'Scheme Announcements', email: false, sms: false, push: true, inApp: true },
    { type: 'System Updates', email: false, sms: false, push: false, inApp: true },
  ]);

  const [quietHours, setQuietHours] = useState<QuietHours>({
    enabled: false,
    startTime: '22:00',
    endTime: '08:00',
  });

  useEffect(() => {
    if (isAuthenticated && user?.id && isValidUUID(user.id)) {
      loadSchemes();
    }
  }, [user?.id, isAuthenticated]);

  const loadSchemes = async () => {
    setLoading(true);
    try {
      const response = await schemeService.getSchemes(0, 100, 'ACTIVE');
      setSchemes(response.content || []);
    } catch (err) {
      console.error('Failed to load schemes:', err);
      showError(t('settings.errors.loadSchemesFailed', { defaultValue: 'Failed to load schemes' }));
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    // Update URL based on tab
    const paths = ['/settings/notifications', '/settings/opt-out'];
    navigate(paths[newValue], { replace: true });
  };

  // Update tab when URL changes and redirect /settings to /settings/notifications
  useEffect(() => {
    if (location.pathname === '/settings') {
      navigate('/settings/notifications', { replace: true });
      return;
    }
    
    const newTab = (() => {
      if (location.pathname.includes('/notifications')) return 0;
      if (location.pathname.includes('/opt-out')) return 1;
      return 0;
    })();
    
    if (newTab !== tabValue) {
      setTabValue(newTab);
    }
  }, [location.pathname, navigate]);

  const handleNotificationPreferenceChange = (
    index: number,
    channel: 'email' | 'sms' | 'push' | 'inApp',
    value: boolean
  ) => {
    const updated = [...notificationPreferences];
    updated[index] = { ...updated[index], [channel]: value };
    setNotificationPreferences(updated);
  };

  const handleSaveNotificationPreferences = async () => {
    setSaving(true);
    try {
      // TODO: Replace with actual API call when backend is ready
      await new Promise((resolve) => setTimeout(resolve, 500));
      showSuccess(t('settings.notifications.saved', { defaultValue: 'Notification preferences saved successfully!' }));
    } catch (err) {
      showError(t('settings.errors.saveFailed', { defaultValue: 'Failed to save preferences' }));
    } finally {
      setSaving(false);
    }
  };

  const handleQuietHoursChange = (field: keyof QuietHours, value: boolean | string) => {
    setQuietHours((prev) => ({ ...prev, [field]: value }));
  };

  const handleOptOutToggle = (schemeId: string) => {
    setOptOutSchemes((prev) => {
      if (prev.includes(schemeId)) {
        return prev.filter((id) => id !== schemeId);
      } else {
        return [...prev, schemeId];
      }
    });
  };

  const handleSaveOptOut = async () => {
    setSaving(true);
    try {
      // TODO: Replace with actual API call when backend is ready
      await new Promise((resolve) => setTimeout(resolve, 500));
      showSuccess(t('settings.optOut.saved', { defaultValue: 'Opt-out preferences saved successfully!' }));
    } catch (err) {
      showError(t('settings.errors.saveFailed', { defaultValue: 'Failed to save preferences' }));
    } finally {
      setSaving(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          {t('settings.notAuthenticated', { defaultValue: 'Please log in to access settings.' })}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('settings.title', { defaultValue: 'Settings' })}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        {t('settings.subtitle', { defaultValue: 'Manage your notification preferences and scheme opt-out settings' })}
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={<NotificationsIcon />}
            iconPosition="start"
            label={t('settings.notifications.title', { defaultValue: 'Notification Preferences' })}
          />
          <Tab
            icon={<OptOutIcon />}
            iconPosition="start"
            label={t('settings.optOut.title', { defaultValue: 'Opt-Out Schemes' })}
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ maxWidth: 900, mx: 'auto' }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {t('settings.notifications.channelPreferences', { defaultValue: 'Channel Preferences' })}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {t('settings.notifications.channelDescription', {
                    defaultValue: 'Choose how you want to receive different types of notifications',
                  })}
                </Typography>
              </Grid>

              {notificationPreferences.map((pref, index) => (
                <Grid item xs={12} key={index}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle1" gutterBottom>
                        {getNotificationTypeLabel(pref.type)}
                      </Typography>
                      <FormGroup row sx={{ mt: 2 }}>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={pref.email}
                              onChange={(e) => handleNotificationPreferenceChange(index, 'email', e.target.checked)}
                            />
                          }
                          label={t('settings.notifications.email', { defaultValue: 'Email' })}
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={pref.sms}
                              onChange={(e) => handleNotificationPreferenceChange(index, 'sms', e.target.checked)}
                            />
                          }
                          label={t('settings.notifications.sms', { defaultValue: 'SMS' })}
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={pref.push}
                              onChange={(e) => handleNotificationPreferenceChange(index, 'push', e.target.checked)}
                            />
                          }
                          label={t('settings.notifications.push', { defaultValue: 'Push' })}
                        />
                        <FormControlLabel
                          control={
                            <Switch
                              checked={pref.inApp}
                              onChange={(e) => handleNotificationPreferenceChange(index, 'inApp', e.target.checked)}
                            />
                          }
                          label={t('settings.notifications.inApp', { defaultValue: 'In-App' })}
                        />
                      </FormGroup>
                    </CardContent>
                  </Card>
                </Grid>
              ))}

              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
              </Grid>

              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  {t('settings.notifications.quietHours', { defaultValue: 'Quiet Hours' })}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {t('settings.notifications.quietHoursDescription', {
                    defaultValue: 'Disable notifications during specific hours',
                  })}
                </Typography>
                <Card variant="outlined">
                  <CardContent>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={quietHours.enabled}
                          onChange={(e) => handleQuietHoursChange('enabled', e.target.checked)}
                        />
                      }
                      label={t('settings.notifications.enableQuietHours', { defaultValue: 'Enable Quiet Hours' })}
                    />
                    {quietHours.enabled && (
                      <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                        <TextField
                          label={t('settings.notifications.startTime', { defaultValue: 'Start Time' })}
                          type="time"
                          value={quietHours.startTime}
                          onChange={(e) => handleQuietHoursChange('startTime', e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                        <TextField
                          label={t('settings.notifications.endTime', { defaultValue: 'End Time' })}
                          type="time"
                          value={quietHours.endTime}
                          onChange={(e) => handleQuietHoursChange('endTime', e.target.value)}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
                  <Button variant="outlined" onClick={() => window.location.reload()}>
                    {t('common.cancel', { defaultValue: 'Cancel' })}
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleSaveNotificationPreferences}
                    disabled={saving}
                    startIcon={<CheckCircleIcon />}
                  >
                    {saving
                      ? t('common.saving', { defaultValue: 'Saving...' })
                      : t('common.save', { defaultValue: 'Save Preferences' })}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ maxWidth: 900, mx: 'auto' }}>
            <Alert severity="info" sx={{ mb: 3 }}>
              {t('settings.optOut.info', {
                defaultValue:
                  'Opting out of a scheme means you will not receive notifications or be automatically considered for that scheme. You can opt back in at any time.',
              })}
            </Alert>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <Typography>{t('common.loading', { defaultValue: 'Loading...' })}</Typography>
              </Box>
            ) : schemes.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <OptOutIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  {t('settings.optOut.noSchemes', { defaultValue: 'No active schemes available' })}
                </Typography>
              </Box>
            ) : (
              <>
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>{t('settings.optOut.schemeName', { defaultValue: 'Scheme Name' })}</TableCell>
                        <TableCell>{t('settings.optOut.category', { defaultValue: 'Category' })}</TableCell>
                        <TableCell>{t('settings.optOut.department', { defaultValue: 'Department' })}</TableCell>
                        <TableCell align="center">{t('settings.optOut.status', { defaultValue: 'Status' })}</TableCell>
                        <TableCell align="center">{t('settings.optOut.action', { defaultValue: 'Action' })}</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {schemes.map((scheme) => (
                        <TableRow key={scheme.id}>
                          <TableCell>
                            <Typography variant="body1">{getSchemeName(scheme, i18n.language)}</Typography>
                          </TableCell>
                          <TableCell>
                            <Chip label={scheme.category ? translateCategory(scheme.category, t) : t('common.none', { defaultValue: 'N/A' })} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>{scheme.department ? translateDepartment(scheme.department, t) : t('common.none', { defaultValue: 'N/A' })}</TableCell>
                          <TableCell align="center">
                            {optOutSchemes.includes(scheme.id) ? (
                              <Chip label={t('settings.optOut.optedOut', { defaultValue: 'Opted Out' })} color="warning" size="small" />
                            ) : (
                              <Chip label={t('settings.optOut.active', { defaultValue: 'Active' })} color="success" size="small" />
                            )}
                          </TableCell>
                          <TableCell align="center">
                            <Checkbox
                              checked={optOutSchemes.includes(scheme.id)}
                              onChange={() => handleOptOutToggle(scheme.id)}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 3 }}>
                  <Button variant="outlined" onClick={() => setOptOutSchemes([])}>
                    {t('settings.optOut.clearAll', { defaultValue: 'Clear All' })}
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleSaveOptOut}
                    disabled={saving}
                    startIcon={<CheckCircleIcon />}
                  >
                    {saving
                      ? t('common.saving', { defaultValue: 'Saving...' })
                      : t('common.save', { defaultValue: 'Save Preferences' })}
                  </Button>
                </Box>
              </>
            )}
          </Box>
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

