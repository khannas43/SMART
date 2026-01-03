import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Container,
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Tabs,
  Tab,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { loginWithOTP, fetchCurrentUser } from '@/store/slices/auth.slice';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

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
      id={`login-tabpanel-${index}`}
      aria-labelledby={`login-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
    </div>
  );
}

const LoginPage: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isLoading, error: authError } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();
  const [activeTab, setActiveTab] = useState(0);
  const [janAadhaar, setJanAadhaar] = useState('');
  const [otp, setOtp] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [otpSent, setOtpSent] = useState(false);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setError(null);
    setOtpSent(false);
  };

  const handleSendOTP = async () => {
    if (!janAadhaar || janAadhaar.length !== 12) {
      setError(t('auth.errors.invalidJanAadhaar'));
      return;
    }

    setError(null);

    try {
      // TODO: Replace with actual OTP API when available
      // await authService.sendOTP(janAadhaar);
      
      // For now, simulate OTP sending
      setOtpSent(true);
      showSuccess(t('auth.otpSent', { defaultValue: 'OTP sent successfully (simulated)' }));
    } catch (err: any) {
      const errorMessage = err.message || t('auth.errors.networkError', { defaultValue: 'Network error' });
      setError(errorMessage);
      showError(errorMessage);
    }
  };

  const handleLogin = async () => {
    if (!otp || otp.length !== 6) {
      setError(t('auth.errors.invalidOTP'));
      return;
    }

    if (!janAadhaar || janAadhaar.length !== 12) {
      setError(t('auth.errors.invalidJanAadhaar'));
      return;
    }

    setError(null);

    try {
      console.log('Starting login with:', { janAadhaar, otp });
      
      // Use OTP verification endpoint (hardcoded OTP: 123456)
      const result = await dispatch(loginWithOTP({ janAadhaarId: janAadhaar, otp })).unwrap();
      
      console.log('OTP verification successful:', result);
      console.log('Token stored:', !!localStorage.getItem('auth_token'));

      // Try to fetch user profile after login
      try {
        const user = await dispatch(fetchCurrentUser()).unwrap();
        console.log('User profile fetched:', user);
      } catch (profileError: any) {
        // Profile fetch failed, but login succeeded - continue with mock user
        console.warn('Failed to fetch user profile (this is okay):', profileError);
        // This is okay - user might need to create profile
      }

      showSuccess(t('auth.loginSuccess', { defaultValue: 'Login successful' }));
      
      // Navigate after a short delay to show success message
      setTimeout(() => {
        console.log('Navigating to /dashboard');
        navigate('/dashboard', { replace: true });
      }, 2000);
    } catch (err: any) {
      console.error('Login error details:', {
        error: err,
        message: err?.message,
        response: err?.response,
        stack: err?.stack
      });
      const errorMessage = err?.message || err || t('auth.errors.genericError', { defaultValue: 'Login failed. Please check your OTP.' });
      setError(errorMessage);
      showError(errorMessage);
    }
  };

  const handleRajSSOLogin = () => {
    // TODO: Implement Raj SSO login
    setError('Raj SSO login not yet implemented');
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          py: 4,
        }}
      >
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            {t('auth.title')}
          </Typography>

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 3 }}>
            <Tabs value={activeTab} onChange={handleTabChange} aria-label="login tabs">
              <Tab label={t('auth.janAadhaarLogin')} id="login-tab-0" aria-controls="login-tabpanel-0" />
              <Tab label={t('auth.rajSSOLogin')} id="login-tab-1" aria-controls="login-tabpanel-1" />
            </Tabs>
          </Box>

          {/* Jan Aadhaar Tab */}
          <TabPanel value={activeTab} index={0}>
            {(error || authError) && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                {error || authError}
              </Alert>
            )}

            {!otpSent ? (
              <>
                <TextField
                  fullWidth
                  label={t('auth.enterJanAadhaar')}
                  placeholder={t('auth.janAadhaarPlaceholder')}
                  value={janAadhaar}
                  onChange={(e) => setJanAadhaar(e.target.value.replace(/\D/g, '').slice(0, 12))}
                  margin="normal"
                  inputProps={{ maxLength: 12 }}
                  helperText={janAadhaar.length !== 12 && janAadhaar.length > 0 ? 'Enter 12 digits' : ''}
                />
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleSendOTP}
                  disabled={isLoading || janAadhaar.length !== 12}
                  sx={{ mt: 2 }}
                >
                  {isLoading ? <CircularProgress size={24} /> : t('auth.sendOTP')}
                </Button>
              </>
            ) : (
              <>
                <Alert severity="info" sx={{ mb: 2 }}>
                  OTP sent to your registered mobile number
                </Alert>
                <TextField
                  fullWidth
                  label={t('auth.enterOTP')}
                  placeholder={t('auth.otpPlaceholder')}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, '').slice(0, 6))}
                  margin="normal"
                  inputProps={{ maxLength: 6 }}
                />
                <Button
                  fullWidth
                  variant="contained"
                  onClick={handleLogin}
                  disabled={isLoading || otp.length !== 6}
                  sx={{ mt: 2 }}
                >
                  {isLoading ? <CircularProgress size={24} /> : t('auth.login')}
                </Button>
                <Button fullWidth onClick={() => setOtpSent(false)} sx={{ mt: 1 }}>
                  {t('auth.resendOTP')}
                </Button>
              </>
            )}
          </TabPanel>

          {/* Raj SSO Tab */}
          <TabPanel value={activeTab} index={1}>
            <Button fullWidth variant="contained" onClick={handleRajSSOLogin} sx={{ mt: 2 }}>
              {t('auth.loginWithRajSSO')}
            </Button>
          </TabPanel>

          {/* Help Links */}
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Button size="small" sx={{ textTransform: 'none' }}>
              {t('auth.forgotJanAadhaar')}
            </Button>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              {t('auth.needHelp')}
            </Typography>
          </Box>
        </Paper>
      </Box>

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

export default LoginPage;

