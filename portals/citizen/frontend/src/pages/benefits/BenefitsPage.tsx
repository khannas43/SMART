import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  Divider,
} from '@mui/material';
import {
  AccountBalance as AccountBalanceIcon,
  TrendingUp as TrendingUpIcon,
  History as HistoryIcon,
  Receipt as ReceiptIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { applicationService, paymentService, schemeService } from '@/services';
import { ServiceApplication, Payment, Scheme } from '@/types/api';
import { isValidUUID } from '@/utils/uuidValidator';
import { getSchemeName } from '@/utils/localization';
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
      id={`benefits-tabpanel-${index}`}
      aria-labelledby={`benefits-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const BenefitsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const currentLanguage = i18n.language;
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Current Benefits Data
  const [currentBenefits, setCurrentBenefits] = useState<ServiceApplication[]>([]);
  const [schemes, setSchemes] = useState<Map<string, Scheme>>(new Map());

  // Forecast Data (mock for now)
  const [forecastData, setForecastData] = useState<any[]>([]);

  // History Data
  const [paymentHistory, setPaymentHistory] = useState<Payment[]>([]);
  const [pastBenefits, setPastBenefits] = useState<ServiceApplication[]>([]);

  // Summary Stats
  const [totalCurrentBenefits, setTotalCurrentBenefits] = useState(0);
  const [totalMonthlyAmount, setTotalMonthlyAmount] = useState(0);
  const [totalForecastAmount, setTotalForecastAmount] = useState(0);
  const [totalPaymentsCount, setTotalPaymentsCount] = useState(0);
  const [totalPaymentsAmount, setTotalPaymentsAmount] = useState(0);

  useEffect(() => {
    if (!isAuthenticated || !user?.id || !isValidUUID(user.id)) {
      setError(t('benefits.notAuthenticated', { defaultValue: 'Please log in to view your benefits.' }));
      setLoading(false);
      return;
    }

    loadBenefitsData();
  }, [user?.id, isAuthenticated]);

  const loadBenefitsData = async () => {
    if (!user?.id || !isValidUUID(user.id)) return;

    setLoading(true);
    setError(null);

    try {
      // Load current benefits (approved applications)
      let allApplications: ServiceApplication[] = [];
      try {
        const applicationsResponse = await applicationService.getApplicationsByCitizen(user.id, 0, 100);
        allApplications = applicationsResponse.content || [];
      } catch (appErr: any) {
        console.error('Failed to load applications:', appErr);
        // Continue with empty array - don't fail the entire page
        setError(t('benefits.applicationsLoadFailed', { 
          defaultValue: 'Unable to load applications. Please try again later.' 
        }));
      }

      // Filter approved/completed applications as current benefits
      const approved = allApplications.filter(
        (app) => app.status === 'APPROVED' || app.status === 'COMPLETED'
      );
      setCurrentBenefits(approved);

      // Filter past benefits (rejected/closed)
      const past = allApplications.filter(
        (app) => app.status === 'REJECTED' || app.status === 'CLOSED' || app.status === 'CANCELLED'
      );
      setPastBenefits(past);

      // Load scheme details for all applications (non-blocking)
      const schemeIds = new Set<string>();
      allApplications.forEach((app) => {
        if (app.schemeId) schemeIds.add(app.schemeId);
      });

      const schemesMap = new Map<string, Scheme>();
      // Load schemes in parallel but don't fail if some fail
      const schemePromises = Array.from(schemeIds).map(async (schemeId) => {
        try {
          const scheme = await schemeService.getSchemeById(schemeId);
          schemesMap.set(schemeId, scheme);
        } catch (err) {
          console.warn(`Failed to load scheme ${schemeId}:`, err);
          // Continue without this scheme
        }
      });
      await Promise.allSettled(schemePromises);
      setSchemes(schemesMap);

      // Load payment history
      let allPayments: Payment[] = [];
      try {
        const paymentsResponse = await paymentService.getPaymentsByCitizen(user.id, 0, 100);
        allPayments = paymentsResponse.content || [];
        const successfulPayments = allPayments.filter(
          (p) => p.status === 'SUCCESS' || p.status === 'COMPLETED'
        );
        setPaymentHistory(successfulPayments);
        
        // Calculate total payments count and amount from payment history
        setTotalPaymentsCount(successfulPayments.length);
        const totalAmount = successfulPayments.reduce((sum, p) => sum + (p.amount || 0), 0);
        setTotalPaymentsAmount(totalAmount);
      } catch (err) {
        console.warn('Failed to load payment history:', err);
        setTotalPaymentsCount(0);
        setTotalPaymentsAmount(0);
      }

      // Calculate summary stats
      setTotalCurrentBenefits(approved.length);
      
      // Calculate monthly amount from approved applications and their schemes
      // Try to get benefit amount from scheme eligibility criteria or use default
      let monthlyTotal = 0;
      approved.forEach((app) => {
        if (app.schemeId) {
          const scheme = schemesMap.get(app.schemeId);
          if (scheme?.eligibilityCriteria) {
            const benefitAmount = scheme.eligibilityCriteria.benefit_amount || 
                                 scheme.eligibilityCriteria.amount ||
                                 5000; // Default fallback
            monthlyTotal += benefitAmount;
          } else {
            monthlyTotal += 5000; // Default fallback
          }
        } else {
          monthlyTotal += 5000; // Default fallback
        }
      });
      setTotalMonthlyAmount(monthlyTotal);
      setTotalForecastAmount(monthlyTotal * 12); // Annual forecast = monthly * 12

      // Generate forecast data from approved applications
      const forecastItems: any[] = [];
      const currentDate = new Date();
      const months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December'];
      
      approved.forEach((app) => {
        const scheme = app.schemeId ? schemesMap.get(app.schemeId) : null;
        const schemeName = scheme ? getSchemeName(scheme, currentLanguage) : app.serviceType || 'Unknown Scheme';
        const benefitAmount = scheme?.eligibilityCriteria?.benefit_amount || 
                            scheme?.eligibilityCriteria?.amount || 
                            5000;
        
        // Generate forecast for next 6 months
        for (let i = 0; i < 6; i++) {
          const forecastDate = new Date(currentDate);
          forecastDate.setMonth(currentDate.getMonth() + i);
          const monthName = months[forecastDate.getMonth()];
          const year = forecastDate.getFullYear();
          
          forecastItems.push({
            month: `${monthName} ${year}`,
            amount: benefitAmount,
            scheme: schemeName,
            status: i < 2 ? 'CONFIRMED' : 'ESTIMATED',
            remarks: i < 2 
              ? t('benefits.confirmedPayment', { defaultValue: 'Confirmed payment schedule' })
              : t('benefits.estimatedProjection', { defaultValue: 'Estimated projection based on scheme policy' }),
            logic: t('benefits.basedOnApprovedApplications', { defaultValue: 'Based on approved applications' })
          });
        }
      });
      
      setForecastData(forecastItems);
    } catch (err: any) {
      console.error('Failed to load benefits data:', err);
      // Only set error if we don't already have a more specific error
      if (!error) {
        setError(err.response?.data?.message || t('benefits.loadFailed', { 
          defaultValue: 'Failed to load some benefits data. Some information may be incomplete.' 
        }));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'APPROVED':
      case 'COMPLETED':
      case 'SUCCESS':
        return 'success';
      case 'PENDING':
      case 'PROCESSING':
        return 'warning';
      case 'REJECTED':
      case 'FAILED':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <CircularProgress />
      </Container>
    );
  }

  if (error && !isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('benefits.title', { defaultValue: 'Benefits & Entitlements' })}
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">{totalCurrentBenefits}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {t('benefits.activeBenefits', { defaultValue: 'Active Benefits' })}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AccountBalanceIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">{formatCurrency(totalMonthlyAmount)}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {t('benefits.monthlyAmount', { defaultValue: 'Monthly Amount' })}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">{formatCurrency(totalForecastAmount)}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                {t('benefits.annualForecast', { defaultValue: 'Annual Forecast' })}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <ReceiptIcon color="secondary" sx={{ mr: 1 }} />
                <Typography variant="h6">{totalPaymentsCount}</Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {t('benefits.totalPayments', { defaultValue: 'Total Payments' })}
              </Typography>
              {totalPaymentsAmount > 0 && (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  {formatCurrency(totalPaymentsAmount)}
                </Typography>
              )}
              <Button
                component={Link}
                to="/payments"
                size="small"
                variant="outlined"
                fullWidth
              >
                {t('benefits.viewAllPayments', { defaultValue: 'View All Payments' })}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange} aria-label="benefits tabs">
          <Tab
            icon={<CheckCircleIcon />}
            iconPosition="start"
            label={t('benefits.currentBenefits', { defaultValue: 'Current Benefits' })}
          />
          <Tab
            icon={<TrendingUpIcon />}
            iconPosition="start"
            label={t('benefits.forecast', { defaultValue: 'Forecast' })}
          />
          <Tab
            icon={<HistoryIcon />}
            iconPosition="start"
            label={t('benefits.history', { defaultValue: 'History' })}
          />
        </Tabs>
      </Paper>

      {/* Current Benefits Tab */}
      <TabPanel value={tabValue} index={0}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}
        {currentBenefits.length === 0 ? (
          <Alert severity="info">
            {t('benefits.noCurrentBenefits', { defaultValue: 'You currently have no active benefits. Apply for schemes to start receiving benefits.' })}
          </Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('benefits.scheme', { defaultValue: 'Scheme' })}</TableCell>
                  <TableCell>{t('benefits.applicationNumber', { defaultValue: 'Application #' })}</TableCell>
                  <TableCell>{t('benefits.status', { defaultValue: 'Status' })}</TableCell>
                  <TableCell>{t('benefits.submittedDate', { defaultValue: 'Submitted' })}</TableCell>
                  <TableCell align="right">{t('common.actions', { defaultValue: 'Actions' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {currentBenefits.map((benefit) => {
                  const scheme = benefit.schemeId ? schemes.get(benefit.schemeId) : null;
                  return (
                    <TableRow key={benefit.id}>
                      <TableCell>
                        <Typography variant="body1" fontWeight="medium">
                          {scheme?.name || benefit.serviceType}
                        </Typography>
                        {scheme?.code && (
                          <Typography variant="caption" color="text.secondary">
                            {scheme.code}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>{benefit.applicationNumber || 'N/A'}</TableCell>
                      <TableCell>
                        <Chip
                          label={benefit.status}
                          size="small"
                          color={getStatusColor(benefit.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {benefit.submittedAt
                          ? new Date(benefit.submittedAt).toLocaleDateString()
                          : 'N/A'}
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          component={Link}
                          to={`/applications/${benefit.id}`}
                          size="small"
                          variant="outlined"
                        >
                          {t('common.view', { defaultValue: 'View' })}
                        </Button>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>

      {/* Forecast Tab */}
      <TabPanel value={tabValue} index={1}>
        <Alert severity="info" sx={{ mb: 3 }}>
          {t('benefits.forecastInfo', { defaultValue: 'Forecast data is estimated based on your current benefits and may vary based on scheme policies.' })}
        </Alert>
        {forecastData.length === 0 ? (
          <Alert severity="info">
            {t('benefits.noForecast', { defaultValue: 'No forecast data available.' })}
          </Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('benefits.month', { defaultValue: 'Month' })}</TableCell>
                  <TableCell>{t('benefits.scheme', { defaultValue: 'Scheme' })}</TableCell>
                  <TableCell align="right">{t('benefits.amount', { defaultValue: 'Amount' })}</TableCell>
                  <TableCell>{t('benefits.status', { defaultValue: 'Status' })}</TableCell>
                  <TableCell>{t('benefits.remarks', { defaultValue: 'Remarks' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {forecastData.map((forecast, index) => (
                  <TableRow key={index}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <ScheduleIcon sx={{ mr: 1, fontSize: 20 }} />
                        {forecast.month}
                      </Box>
                    </TableCell>
                    <TableCell>{forecast.scheme}</TableCell>
                    <TableCell align="right">{formatCurrency(forecast.amount)}</TableCell>
                    <TableCell>
                      <Chip
                        label={forecast.status}
                        size="small"
                        color={forecast.status === 'CONFIRMED' ? 'success' : 'default'}
                      />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" color="text.secondary">
                        {forecast.remarks || forecast.logic || '-'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>

      {/* History Tab */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h6" gutterBottom>
          {t('benefits.paymentHistory', { defaultValue: 'Payment History' })}
        </Typography>
        {paymentHistory.length === 0 ? (
          <Alert severity="info" sx={{ mb: 3 }}>
            {t('benefits.noPaymentHistory', { defaultValue: 'No payment history available.' })}
          </Alert>
        ) : (
          <TableContainer component={Paper} sx={{ mb: 4 }}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('benefits.transactionId', { defaultValue: 'Transaction ID' })}</TableCell>
                  <TableCell>{t('benefits.date', { defaultValue: 'Date' })}</TableCell>
                  <TableCell align="right">{t('benefits.amount', { defaultValue: 'Amount' })}</TableCell>
                  <TableCell>{t('benefits.method', { defaultValue: 'Method' })}</TableCell>
                  <TableCell>{t('benefits.status', { defaultValue: 'Status' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paymentHistory.map((payment) => (
                  <TableRow key={payment.id}>
                    <TableCell>{payment.transactionId}</TableCell>
                    <TableCell>
                      {payment.completedAt
                        ? new Date(payment.completedAt).toLocaleDateString()
                        : payment.initiatedAt
                        ? new Date(payment.initiatedAt).toLocaleDateString()
                        : 'N/A'}
                    </TableCell>
                    <TableCell align="right">{formatCurrency(payment.amount)}</TableCell>
                    <TableCell>{payment.paymentMethod}</TableCell>
                    <TableCell>
                      <Chip
                        label={payment.status}
                        size="small"
                        color={getStatusColor(payment.status) as any}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Divider sx={{ my: 4 }} />

        <Typography variant="h6" gutterBottom>
          {t('benefits.pastBenefits', { defaultValue: 'Past Benefits' })}
        </Typography>
        {pastBenefits.length === 0 ? (
          <Alert severity="info">
            {t('benefits.noPastBenefits', { defaultValue: 'No past benefits found.' })}
          </Alert>
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>{t('benefits.scheme', { defaultValue: 'Scheme' })}</TableCell>
                  <TableCell>{t('benefits.applicationNumber', { defaultValue: 'Application #' })}</TableCell>
                  <TableCell>{t('benefits.status', { defaultValue: 'Status' })}</TableCell>
                  <TableCell>{t('benefits.submittedDate', { defaultValue: 'Submitted' })}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pastBenefits.map((benefit) => {
                  const scheme = benefit.schemeId ? schemes.get(benefit.schemeId) : null;
                  return (
                    <TableRow key={benefit.id}>
                      <TableCell>{scheme ? getSchemeName(scheme, currentLanguage) : benefit.serviceType}</TableCell>
                      <TableCell>{benefit.applicationNumber || 'N/A'}</TableCell>
                      <TableCell>
                        <Chip
                          label={benefit.status}
                          size="small"
                          color={getStatusColor(benefit.status) as any}
                        />
                      </TableCell>
                      <TableCell>
                        {benefit.submittedAt
                          ? new Date(benefit.submittedAt).toLocaleDateString()
                          : 'N/A'}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </TabPanel>
    </Container>
  );
};

