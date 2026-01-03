import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Pagination,
  Tabs,
  Tab,
  Tooltip,
} from '@mui/material';
import {
  Payment as PaymentIcon,
  Receipt as ReceiptIcon,
  Download as DownloadIcon,
  Add as AddIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  CheckCircle as SuccessIcon,
  Cancel as FailedIcon,
  HourglassEmpty as PendingIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { paymentService } from '@/services/payment.service';
import { applicationService } from '@/services/application.service';
import { Payment, PaymentRequest, ServiceApplication } from '@/types/api';
import { isValidUUID } from '@/utils/uuidValidator';
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
      id={`payment-tabpanel-${index}`}
      aria-labelledby={`payment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export const PaymentsPage: React.FC = () => {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showError, showSuccess, close } = useMessageDialog();
  const [searchParams] = useSearchParams();
  const applicationIdFromUrl = searchParams.get('applicationId');
  const serviceRequestIdFromUrl = searchParams.get('serviceRequestId');
  const amountFromUrl = searchParams.get('amount');
  const serviceNameFromUrl = searchParams.get('serviceName');

  const [tabValue, setTabValue] = useState(applicationIdFromUrl || serviceRequestIdFromUrl ? 1 : 0); // 0: History, 1: Make Payment
  const [loading, setLoading] = useState(false);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [applications, setApplications] = useState<ServiceApplication[]>([]);
  const [serviceRequests, setServiceRequests] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [size, setSize] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Sorting state
  const [sortField, setSortField] = useState<keyof Payment | 'applicationType'>('initiatedAt');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Payment Dialog State
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState<ServiceApplication | null>(null);
  const [paymentForm, setPaymentForm] = useState<PaymentRequest>({
    applicationId: undefined,
    amount: 0,
    currency: 'INR',
    paymentMethod: 'UPI',
    description: '',
  });

  useEffect(() => {
    if (isAuthenticated && user?.id && isValidUUID(user.id)) {
      loadPayments();
    }
  }, [user?.id, isAuthenticated, page, size, filterStatus, sortField, sortOrder]);

  useEffect(() => {
    if (isAuthenticated && user?.id && isValidUUID(user.id)) {
      loadApplications();
      loadServiceRequests();
    }
  }, [user?.id, isAuthenticated]);

  // Handle applicationId from URL after applications are loaded
  useEffect(() => {
    if (applicationIdFromUrl && applications.length > 0) {
      const app = applications.find((a) => a.id === applicationIdFromUrl);
      if (app) {
        setSelectedApplication(app);
        setPaymentForm((prev) => ({
          ...prev,
          applicationId: app.id,
          description: `Payment for application ${app.applicationNumber}`,
        }));
        setTabValue(1); // Switch to Make Payment tab
      }
    }
  }, [applicationIdFromUrl, applications]);

  // Handle serviceRequestId from URL
  useEffect(() => {
    if (serviceRequestIdFromUrl) {
      const amount = amountFromUrl ? parseFloat(amountFromUrl) : 0;
      const serviceName = serviceNameFromUrl ? decodeURIComponent(serviceNameFromUrl) : 'Service Request';
      setPaymentForm((prev) => ({
        ...prev,
        applicationId: undefined, // Service requests don't have applicationId
        amount: amount,
        description: `Payment for ${serviceName}`,
      }));
      setTabValue(1); // Switch to Make Payment tab
    }
  }, [serviceRequestIdFromUrl, amountFromUrl, serviceNameFromUrl]);

  const loadPayments = async () => {
    if (!user?.id || !isValidUUID(user.id)) return;

    setLoading(true);
    try {
      const response = await paymentService.getPaymentsByCitizen(user.id, page, size);
      let filteredPayments = response.content || [];

      // Apply status filter
      if (filterStatus !== 'ALL') {
        filteredPayments = filteredPayments.filter((p) => p.status === filterStatus);
      }

      // Apply search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        filteredPayments = filteredPayments.filter(
          (p) =>
            p.transactionId.toLowerCase().includes(query) ||
            p.description?.toLowerCase().includes(query) ||
            p.paymentMethod.toLowerCase().includes(query)
        );
      }

      // Sort payments
      const sortedPayments = [...filteredPayments].sort((a, b) => {
        let aValue: any;
        let bValue: any;

        if (sortField === 'applicationType') {
          // For application type, we'll get it from description
          aValue = a.description || '';
          bValue = b.description || '';
        } else {
          aValue = a[sortField as keyof Payment];
          bValue = b[sortField as keyof Payment];
        }

        // Handle dates
        if (sortField === 'initiatedAt' || sortField === 'createdAt') {
          aValue = aValue ? new Date(aValue).getTime() : 0;
          bValue = bValue ? new Date(bValue).getTime() : 0;
        }

        // Handle strings
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          aValue = aValue.toLowerCase();
          bValue = bValue.toLowerCase();
        }

        if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });

      setPayments(sortedPayments);
      setTotalPages(response.totalPages || 0);
      setTotalElements(response.totalElements || 0);
    } catch (err: any) {
      console.error('Failed to load payments:', err);
      showError(t('payments.errors.loadFailed', { defaultValue: 'Failed to load payment history' }));
    } finally {
      setLoading(false);
    }
  };

  const loadApplications = async () => {
    if (!user?.id || !isValidUUID(user.id)) return;

    try {
      const response = await applicationService.getApplicationsByCitizen(user.id, 0, 100);
      // Filter to only show applications with pending payments (no successful payment yet)
      const allPayments = await paymentService.getPaymentsByCitizen(user.id, 0, 1000);
      const successfulPaymentAppIds = new Set(
        (allPayments.content || [])
          .filter((p) => p.status === 'SUCCESS' || p.status === 'COMPLETED')
          .map((p) => p.applicationId)
          .filter((id): id is string => !!id)
      );

      // Show applications that don't have successful payments yet
      const pendingApplications = (response.content || []).filter(
        (app) => !successfulPaymentAppIds.has(app.id) && (app.status === 'SUBMITTED' || app.status === 'UNDER_REVIEW' || app.status === 'APPROVED')
      );
      setApplications(pendingApplications);
    } catch (err) {
      console.error('Failed to load applications:', err);
    }
  };

  const loadServiceRequests = async () => {
    // Load service requests from localStorage (same storage as ServicesPage uses)
    if (!user?.id || !isValidUUID(user.id)) return;

    try {
      // Load all service requests from localStorage
      const storedRequests = localStorage.getItem('serviceRequests');
      let allServiceRequests: any[] = [];
      
      if (storedRequests) {
        try {
          allServiceRequests = JSON.parse(storedRequests);
        } catch (err) {
          console.error('Failed to parse stored service requests:', err);
        }
      }

      // Get all payments to check which service requests have successful payments
      const allPayments = await paymentService.getPaymentsByCitizen(user.id, 0, 1000);
      const successfulPaymentDescriptions = new Set(
        (allPayments.content || [])
          .filter((p) => p.status === 'SUCCESS' || p.status === 'COMPLETED')
          .map((p) => p.description || '')
      );

      // Filter to only show service requests with pending payments (no successful payment and has fees)
      const pendingServiceRequests = allServiceRequests
        .filter((sr) => {
          // Check if this service request has a successful payment
          const hasSuccessfulPayment = Array.from(successfulPaymentDescriptions).some((desc) =>
            desc.includes(sr.serviceName) || desc.includes(sr.requestNumber) || (sr.transactionId && desc.includes(sr.transactionId))
          );
          
          // Also check if the service request itself has a successful payment status
          const hasPaymentSuccess = sr.paymentStatus === 'SUCCESS' || sr.paymentStatus === 'COMPLETED';
          
          // Show if: has fees, no successful payment, and status is not COMPLETED/CANCELLED
          return (
            (sr.fees && sr.fees > 0) &&
            !hasSuccessfulPayment &&
            !hasPaymentSuccess &&
            sr.status !== 'COMPLETED' &&
            sr.status !== 'CANCELLED'
          );
        })
        .map((sr) => ({
          id: sr.id,
          type: 'SERVICE_REQUEST',
          name: sr.serviceName || 'Service Request',
          requestNumber: sr.requestNumber,
          fees: sr.fees || 0,
          status: sr.status,
        }));

      console.log('Loaded service requests for payment dropdown:', { 
        pendingServiceRequests, 
        count: pendingServiceRequests.length,
        ids: pendingServiceRequests.map(sr => ({ id: sr.id, type: typeof sr.id, stringId: String(sr.id), menuValue: `sr-${String(sr.id)}` }))
      });
      setServiceRequests(pendingServiceRequests);
    } catch (err) {
      console.error('Failed to load service requests:', err);
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleMakePayment = (application?: ServiceApplication) => {
    if (application) {
      setSelectedApplication(application);
      setPaymentForm({
        applicationId: application.id,
        amount: 0, // Will be set based on scheme or application
        currency: 'INR',
        paymentMethod: 'UPI',
        description: `Payment for application ${application.applicationNumber}`,
      });
    } else {
      setSelectedApplication(null);
      setPaymentForm({
        applicationId: undefined,
        amount: 0,
        currency: 'INR',
        paymentMethod: 'UPI',
        description: '',
      });
    }
    setShowPaymentDialog(true);
  };

  const handleSubmitPayment = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      showError(t('payments.errors.notAuthenticated', { defaultValue: 'Please log in to make a payment' }));
      return;
    }

    // Check if it's an application or service request
    const isServiceRequest = paymentForm.applicationId?.startsWith('sr-');
    const isApplication = paymentForm.applicationId?.startsWith('app-');
    
    if (!paymentForm.applicationId || (!isApplication && !isServiceRequest)) {
      showError(t('payments.errors.selectApplication', { defaultValue: 'Please select an application or service request' }));
      return;
    }

    if (!paymentForm.amount || paymentForm.amount <= 0) {
      showError(t('payments.errors.invalidAmount', { defaultValue: 'Please enter a valid amount' }));
      return;
    }

    if (!paymentForm.paymentMethod) {
      showError(t('payments.errors.selectMethod', { defaultValue: 'Please select a payment method' }));
      return;
    }

    setLoading(true);
    try {
      // Extract actual ID from prefixed value
      let actualApplicationId: string | undefined = undefined;
      let serviceRequestId: string | undefined = undefined;
      
      if (paymentForm.applicationId?.startsWith('app-')) {
        actualApplicationId = paymentForm.applicationId.replace('app-', '');
      } else if (paymentForm.applicationId?.startsWith('sr-')) {
        serviceRequestId = paymentForm.applicationId.replace('sr-', '');
      }
      
      const paymentData: PaymentRequest = {
        applicationId: actualApplicationId,
        serviceRequestId: serviceRequestId,
        amount: paymentForm.amount,
        currency: paymentForm.currency || 'INR',
        paymentMethod: paymentForm.paymentMethod,
        description: paymentForm.description,
      };
      const payment = await paymentService.initiatePayment(user.id, paymentData);
      
      // If payment is for a service request, update the service request in localStorage
      if (serviceRequestId) {
        const storedRequests = localStorage.getItem('serviceRequests');
        if (storedRequests) {
          try {
            const allServiceRequests = JSON.parse(storedRequests);
            const updatedRequests = allServiceRequests.map((sr: any) => {
              if (sr.id === serviceRequestId) {
                return {
                  ...sr,
                  transactionId: payment.transactionId,
                  paymentStatus: payment.status,
                  paymentDate: payment.initiatedAt || payment.createdAt,
                };
              }
              return sr;
            });
            localStorage.setItem('serviceRequests', JSON.stringify(updatedRequests));
          } catch (err) {
            console.error('Failed to update service request in localStorage:', err);
          }
        }
      }
      
      showSuccess(t('payments.success.initiated', { defaultValue: 'Payment initiated successfully!' }));
      setShowPaymentDialog(false);
      setPaymentForm({
        applicationId: undefined,
        amount: 0,
        currency: 'INR',
        paymentMethod: 'UPI',
        description: '',
      });
      setSelectedApplication(null);
      loadPayments();
      loadServiceRequests(); // Reload service requests to reflect payment status
    } catch (err: any) {
      console.error('Failed to initiate payment:', err);
      showError(err?.response?.data?.message || t('payments.errors.initiateFailed', { defaultValue: 'Failed to initiate payment' }));
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toUpperCase()) {
      case 'SUCCESS':
      case 'COMPLETED':
        return <SuccessIcon color="success" />;
      case 'FAILED':
      case 'CANCELLED':
        return <FailedIcon color="error" />;
      case 'PENDING':
      case 'PROCESSING':
        return <PendingIcon color="warning" />;
      default:
        return <PendingIcon color="info" />;
    }
  };

  const getStatusColor = (status: string): 'success' | 'error' | 'warning' | 'info' => {
    switch (status.toUpperCase()) {
      case 'SUCCESS':
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
      case 'CANCELLED':
        return 'error';
      case 'PENDING':
      case 'PROCESSING':
        return 'warning';
      default:
        return 'info';
    }
  };

  const getStatusLabel = (status: string): string => {
    const statusMap: Record<string, string> = {
      SUCCESS: t('payments.status.success', { defaultValue: 'Success' }),
      COMPLETED: t('payments.status.completed', { defaultValue: 'Completed' }),
      PENDING: t('payments.status.pending', { defaultValue: 'Pending' }),
      PROCESSING: t('payments.status.processing', { defaultValue: 'Processing' }),
      FAILED: t('payments.status.failed', { defaultValue: 'Failed' }),
      CANCELLED: t('payments.status.cancelled', { defaultValue: 'Cancelled' }),
    };
    return statusMap[status.toUpperCase()] || status;
  };

  const getPaymentMethodLabel = (method: string): string => {
    const methodMap: Record<string, string> = {
      UPI: t('payments.method.upi', { defaultValue: 'UPI' }),
      NET_BANKING: t('payments.method.netBanking', { defaultValue: 'Net Banking' }),
      DEBIT_CARD: t('payments.method.debitCard', { defaultValue: 'Debit Card' }),
      CREDIT_CARD: t('payments.method.creditCard', { defaultValue: 'Credit Card' }),
      WALLET: t('payments.method.wallet', { defaultValue: 'Wallet' }),
    };
    return methodMap[method.toUpperCase()] || method;
  };

  const formatCurrency = (amount: number, currency: string = 'INR') => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleDownloadReceipt = async (payment: Payment) => {
    try {
      // Get application if payment is linked to one
      let application: ServiceApplication | null = null;
      if (payment.applicationId) {
        try {
          application = await applicationService.getApplicationById(payment.applicationId);
        } catch (err) {
          console.warn('Could not fetch application for receipt:', err);
        }
      }
      
      // Use the receipt generator that opens print dialog for PDF download
      const { generatePaymentReceiptPdf } = await import('@/utils/receiptGenerator');
      generatePaymentReceiptPdf(payment, application, t);
      
      // Show success message after a short delay
      setTimeout(() => {
        showSuccess(t('payments.receipt.downloadSuccess', { defaultValue: 'Receipt opened. Use Print dialog to save as PDF.' }));
      }, 500);
    } catch (error) {
      console.error('Error generating receipt:', error);
      showError(t('payments.receipt.downloadFailed', { defaultValue: 'Failed to download receipt' }));
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          {t('payments.notAuthenticated', { defaultValue: 'Please log in to view your payments.' })}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          {t('payments.title', { defaultValue: 'Payments' })}
        </Typography>
      </Box>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={<ReceiptIcon />}
            iconPosition="start"
            label={t('payments.history', { defaultValue: 'Payment History' })}
          />
          <Tab
            icon={<PaymentIcon />}
            iconPosition="start"
            label={t('payments.makePaymentLabel', { defaultValue: 'Make Payment' })}
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          {/* Filters */}
          <Box sx={{ p: 2, display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            <TextField
              size="small"
              placeholder={t('payments.search', { defaultValue: 'Search transactions...' })}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ flexGrow: 1, minWidth: 200 }}
            />
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>{t('payments.filter.status', { defaultValue: 'Status' })}</InputLabel>
              <Select
                value={filterStatus}
                label={t('payments.filter.status', { defaultValue: 'Status' })}
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="ALL">{t('payments.filter.all', { defaultValue: 'All' })}</MenuItem>
                <MenuItem value="SUCCESS">{t('payments.status.success', { defaultValue: 'Success' })}</MenuItem>
                <MenuItem value="PENDING">{t('payments.status.pending', { defaultValue: 'Pending' })}</MenuItem>
                <MenuItem value="PROCESSING">{t('payments.status.processing', { defaultValue: 'Processing' })}</MenuItem>
                <MenuItem value="FAILED">{t('payments.status.failed', { defaultValue: 'Failed' })}</MenuItem>
              </Select>
            </FormControl>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadPayments}
              disabled={loading}
            >
              {t('common.refresh', { defaultValue: 'Refresh' })}
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : payments.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ReceiptIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('payments.noPayments', { defaultValue: 'No payments found' })}
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleMakePayment()}
                sx={{ mt: 2 }}
              >
                {t('payments.makePaymentLabel', { defaultValue: 'Make Payment' })}
              </Button>
            </Box>
          ) : (
            <>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'initiatedAt' || sortField === 'createdAt'}
                          direction={(sortField === 'initiatedAt' || sortField === 'createdAt') ? sortOrder : 'desc'}
                          onClick={() => {
                            const field = sortField === 'initiatedAt' || sortField === 'createdAt' ? 'initiatedAt' : 'initiatedAt';
                            setSortField(field);
                            setSortOrder(sortField === field && sortOrder === 'desc' ? 'asc' : 'desc');
                          }}
                        >
                          {t('payments.table.date', { defaultValue: 'Date' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'transactionId'}
                          direction={sortField === 'transactionId' ? sortOrder : 'asc'}
                          onClick={() => {
                            setSortField('transactionId');
                            setSortOrder(sortField === 'transactionId' && sortOrder === 'asc' ? 'desc' : 'asc');
                          }}
                        >
                          {t('payments.table.transactionId', { defaultValue: 'Transaction ID' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'applicationType'}
                          direction={sortField === 'applicationType' ? sortOrder : 'asc'}
                          onClick={() => {
                            setSortField('applicationType');
                            setSortOrder(sortField === 'applicationType' && sortOrder === 'asc' ? 'desc' : 'asc');
                          }}
                        >
                          {t('payments.table.applicationType', { defaultValue: 'Application Type' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'amount'}
                          direction={sortField === 'amount' ? sortOrder : 'asc'}
                          onClick={() => {
                            setSortField('amount');
                            setSortOrder(sortField === 'amount' && sortOrder === 'asc' ? 'desc' : 'asc');
                          }}
                        >
                          {t('payments.table.amount', { defaultValue: 'Amount' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'paymentMethod'}
                          direction={sortField === 'paymentMethod' ? sortOrder : 'asc'}
                          onClick={() => {
                            setSortField('paymentMethod');
                            setSortOrder(sortField === 'paymentMethod' && sortOrder === 'asc' ? 'desc' : 'asc');
                          }}
                        >
                          {t('payments.table.method', { defaultValue: 'Method' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell>
                        <TableSortLabel
                          active={sortField === 'status'}
                          direction={sortField === 'status' ? sortOrder : 'asc'}
                          onClick={() => {
                            setSortField('status');
                            setSortOrder(sortField === 'status' && sortOrder === 'asc' ? 'desc' : 'asc');
                          }}
                        >
                          {t('payments.table.status', { defaultValue: 'Status' })}
                        </TableSortLabel>
                      </TableCell>
                      <TableCell align="center">{t('payments.table.actions', { defaultValue: 'Actions' })}</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payments.map((payment) => {
                      // Get application type from description or application
                      let applicationType = t('payments.standalone', { defaultValue: 'Standalone Payment' });
                      if (payment.applicationId) {
                        const app = applications.find((a) => a.id === payment.applicationId);
                        applicationType = app?.serviceType || applicationType;
                      } else if (payment.description) {
                        // Try to extract service request name from description
                        if (payment.description.includes('Service Request') || payment.description.includes('SR-')) {
                          applicationType = payment.description;
                        } else {
                          applicationType = payment.description;
                        }
                      }

                      return (
                        <TableRow key={payment.id}>
                          <TableCell>
                            <Typography variant="body2">{formatDate(payment.initiatedAt || payment.createdAt)}</Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontFamily="monospace">
                              {payment.transactionId}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">{applicationType}</Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body1" fontWeight="bold">
                              {formatCurrency(payment.amount, payment.currency)}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip label={getPaymentMethodLabel(payment.paymentMethod)} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>
                            <Chip
                              icon={getStatusIcon(payment.status)}
                              label={getStatusLabel(payment.status)}
                              color={getStatusColor(payment.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Tooltip title={t('payments.receipt.downloadTooltip', { defaultValue: 'Download Receipt' })}>
                              <span>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDownloadReceipt(payment)}
                                  disabled={payment.status !== 'SUCCESS' && payment.status !== 'COMPLETED'}
                                  aria-label={t('payments.receipt.downloadTooltip', { defaultValue: 'Download Receipt' })}
                                >
                                  <DownloadIcon />
                                </IconButton>
                              </span>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
              {totalPages > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <Pagination
                    count={totalPages}
                    page={page + 1}
                    onChange={(_, newPage) => setPage(newPage - 1)}
                    color="primary"
                  />
                </Box>
              )}
            </>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ maxWidth: 600, mx: 'auto', p: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('payments.makePayment.title', { defaultValue: 'Initiate New Payment' })}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              {t('payments.makePayment.description', {
                defaultValue: 'Make a payment for an application or standalone payment',
              })}
            </Typography>

            {serviceRequestIdFromUrl && (
              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body2">
                  <strong>{t('services.paymentForService', { defaultValue: 'Payment for Service Request' })}:</strong>{' '}
                  {serviceNameFromUrl ? decodeURIComponent(serviceNameFromUrl) : 'Service Request'}
                </Typography>
              </Alert>
            )}

            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth required>
                  <InputLabel>{t('payments.form.application', { defaultValue: 'Application / Service Request' })}</InputLabel>
                  <Select
                    value={paymentForm.applicationId || (serviceRequestIdFromUrl ? `sr-${serviceRequestIdFromUrl}` : '')}
                    label={t('payments.form.application', { defaultValue: 'Application / Service Request' })}
                    onChange={(e) => {
                      const value = e.target.value;
                      console.log('Select onChange triggered:', { value, serviceRequests, applications });
                      if (value.startsWith('app-')) {
                        const appId = value.replace('app-', '');
                        const app = applications.find((a) => a.id === appId);
                        setPaymentForm((prev) => ({
                          ...prev,
                          applicationId: value,
                          description: app ? `Payment for application ${app.applicationNumber}` : prev.description,
                        }));
                      } else if (value.startsWith('sr-')) {
                        const srId = value.replace('sr-', '');
                        // Try to find by string comparison since IDs might be strings or numbers
                        const sr = serviceRequests.find((s) => String(s.id) === String(srId));
                        console.log('Selected service request:', { 
                          srId, 
                          sr, 
                          allServiceRequests: serviceRequests,
                          serviceRequestIds: serviceRequests.map(s => ({ id: s.id, type: typeof s.id, stringId: String(s.id) }))
                        });
                        if (sr) {
                          setPaymentForm((prev) => ({
                            ...prev,
                            applicationId: value,
                            amount: sr.fees || prev.amount,
                            description: `Payment for ${sr.name} - ${sr.requestNumber}`,
                          }));
                        } else {
                          console.error('Service request not found:', { 
                            srId, 
                            searchedId: srId,
                            availableIds: serviceRequests.map(s => s.id),
                            availableIdsTypes: serviceRequests.map(s => ({ id: s.id, type: typeof s.id, stringId: String(s.id) }))
                          });
                        }
                      }
                    }}
                    disabled={false}
                    required
                    displayEmpty
                  >
                    <MenuItem value="" disabled>
                      {t('payments.form.selectApplication', { defaultValue: 'Select Application or Service Request' })}
                    </MenuItem>
                    {applications.length > 0 && (
                      <MenuItem disabled sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                        {t('payments.applications', { defaultValue: 'Applications' })}
                      </MenuItem>
                    )}
                    {applications.map((app) => (
                      <MenuItem key={app.id} value={`app-${app.id}`}>
                        {app.applicationNumber} - {app.serviceType}
                      </MenuItem>
                    ))}
                    {serviceRequests.length > 0 && (
                      <MenuItem disabled sx={{ fontWeight: 'bold', color: 'text.primary' }}>
                        {t('payments.serviceRequests', { defaultValue: 'Service Requests' })}
                      </MenuItem>
                    )}
                    {serviceRequests.map((sr) => {
                      // Ensure ID is converted to string for consistent comparison
                      const menuValue = `sr-${String(sr.id)}`;
                      return (
                        <MenuItem 
                          key={`sr-menu-${String(sr.id)}`} 
                          value={menuValue}
                        >
                          {sr.requestNumber} - {sr.name} (₹{sr.fees})
                        </MenuItem>
                      );
                    })}
                    {applications.length === 0 && serviceRequests.length === 0 && (
                      <MenuItem value="" disabled>
                        {t('payments.noPendingPayments', { defaultValue: 'No pending payments found' })}
                      </MenuItem>
                    )}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('payments.form.amount', { defaultValue: 'Amount' })}
                  type="number"
                  value={paymentForm.amount || ''}
                  onChange={(e) =>
                    setPaymentForm((prev) => ({
                      ...prev,
                      amount: parseFloat(e.target.value) || 0,
                    }))
                  }
                  InputProps={{
                    startAdornment: <Typography sx={{ mr: 1 }}>₹</Typography>,
                  }}
                  required
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>{t('payments.form.currency', { defaultValue: 'Currency' })}</InputLabel>
                  <Select
                    value={paymentForm.currency || 'INR'}
                    label={t('payments.form.currency', { defaultValue: 'Currency' })}
                    onChange={(e) => setPaymentForm((prev) => ({ ...prev, currency: e.target.value }))}
                  >
                    <MenuItem value="INR">INR (₹)</MenuItem>
                    <MenuItem value="USD">USD ($)</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel>{t('payments.form.method', { defaultValue: 'Payment Method' })}</InputLabel>
                  <Select
                    value={paymentForm.paymentMethod}
                    label={t('payments.form.method', { defaultValue: 'Payment Method' })}
                    onChange={(e) => setPaymentForm((prev) => ({ ...prev, paymentMethod: e.target.value }))}
                  >
                    <MenuItem value="UPI">{t('payments.method.upi', { defaultValue: 'UPI' })}</MenuItem>
                    <MenuItem value="NET_BANKING">{t('payments.method.netBanking', { defaultValue: 'Net Banking' })}</MenuItem>
                    <MenuItem value="DEBIT_CARD">{t('payments.method.debitCard', { defaultValue: 'Debit Card' })}</MenuItem>
                    <MenuItem value="CREDIT_CARD">{t('payments.method.creditCard', { defaultValue: 'Credit Card' })}</MenuItem>
                    <MenuItem value="WALLET">{t('payments.method.wallet', { defaultValue: 'Wallet' })}</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('payments.form.description', { defaultValue: 'Description (Optional)' })}
                  multiline
                  rows={3}
                  value={paymentForm.description || ''}
                  onChange={(e) => setPaymentForm((prev) => ({ ...prev, description: e.target.value }))}
                />
              </Grid>

              <Grid item xs={12}>
                <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                  <Button variant="outlined" onClick={() => setShowPaymentDialog(false)}>
                    {t('common.cancel', { defaultValue: 'Cancel' })}
                  </Button>
                  <Button
                    variant="contained"
                    onClick={handleSubmitPayment}
                    disabled={loading || !paymentForm.applicationId || !paymentForm.amount || !paymentForm.paymentMethod}
                    startIcon={<PaymentIcon />}
                  >
                    {loading
                      ? t('common.processing', { defaultValue: 'Processing...' })
                      : t('payments.submit', { defaultValue: 'Initiate Payment' })}
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </Box>
        </TabPanel>
      </Paper>

      {/* Make Payment Dialog (Alternative - can be triggered from History tab) */}
      <Dialog open={showPaymentDialog} onClose={() => setShowPaymentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{t('payments.makePayment.title', { defaultValue: 'Initiate New Payment' })}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>{t('payments.form.application', { defaultValue: 'Application (Optional)' })}</InputLabel>
                <Select
                  value={paymentForm.applicationId || ''}
                  label={t('payments.form.application', { defaultValue: 'Application (Optional)' })}
                  onChange={(e) =>
                    setPaymentForm((prev) => ({
                      ...prev,
                      applicationId: e.target.value || undefined,
                    }))
                  }
                >
                  <MenuItem value="">{t('payments.form.none', { defaultValue: 'None (Standalone Payment)' })}</MenuItem>
                  {applications.map((app) => (
                    <MenuItem key={app.id} value={app.id}>
                      {app.applicationNumber} - {app.serviceType}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('payments.form.amount', { defaultValue: 'Amount' })}
                type="number"
                value={paymentForm.amount || ''}
                onChange={(e) =>
                  setPaymentForm((prev) => ({
                    ...prev,
                    amount: parseFloat(e.target.value) || 0,
                  }))
                }
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('payments.form.currency', { defaultValue: 'Currency' })}</InputLabel>
                <Select
                  value={paymentForm.currency || 'INR'}
                  label={t('payments.form.currency', { defaultValue: 'Currency' })}
                  onChange={(e) => setPaymentForm((prev) => ({ ...prev, currency: e.target.value }))}
                >
                  <MenuItem value="INR">INR</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>{t('payments.form.method', { defaultValue: 'Payment Method' })}</InputLabel>
                <Select
                  value={paymentForm.paymentMethod}
                  label={t('payments.form.method', { defaultValue: 'Payment Method' })}
                  onChange={(e) => setPaymentForm((prev) => ({ ...prev, paymentMethod: e.target.value }))}
                >
                  <MenuItem value="UPI">{t('payments.method.upi', { defaultValue: 'UPI' })}</MenuItem>
                  <MenuItem value="NET_BANKING">{t('payments.method.netBanking', { defaultValue: 'Net Banking' })}</MenuItem>
                  <MenuItem value="DEBIT_CARD">{t('payments.method.debitCard', { defaultValue: 'Debit Card' })}</MenuItem>
                  <MenuItem value="CREDIT_CARD">{t('payments.method.creditCard', { defaultValue: 'Credit Card' })}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('payments.form.description', { defaultValue: 'Description (Optional)' })}
                multiline
                rows={2}
                value={paymentForm.description || ''}
                onChange={(e) => setPaymentForm((prev) => ({ ...prev, description: e.target.value }))}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPaymentDialog(false)}>{t('common.cancel', { defaultValue: 'Cancel' })}</Button>
          <Button
            variant="contained"
            onClick={handleSubmitPayment}
            disabled={loading || !paymentForm.amount || !paymentForm.paymentMethod}
          >
            {loading
              ? t('common.processing', { defaultValue: 'Processing...' })
              : t('payments.submit', { defaultValue: 'Initiate Payment' })}
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

