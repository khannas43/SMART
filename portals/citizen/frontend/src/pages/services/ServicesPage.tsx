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
  CardActions,
  Button,
  Chip,
  TextField,
  InputAdornment,
  MenuItem,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  Build as ServiceIcon,
  Add as AddIcon,
  CheckCircle as CompletedIcon,
  HourglassEmpty as PendingIcon,
  Cancel as CancelledIcon,
  Info as InfoIcon,
  ArrowForward as ArrowForwardIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Payment as PaymentIcon,
  Description as DocumentIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '@/store/hooks';
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
      id={`services-tabpanel-${index}`}
      aria-labelledby={`services-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface Service {
  id: string;
  name: string;
  nameHindi?: string;
  description: string;
  descriptionHindi?: string;
  category: string;
  categoryHindi?: string;
  department: string;
  departmentHindi?: string;
  icon?: string;
  estimatedTime?: string;
  estimatedTimeHindi?: string;
  requiredDocuments?: string[];
  requiredDocumentsHindi?: string[];
  fees?: number;
  isActive: boolean;
}

interface ServiceRequest {
  id: string;
  serviceId: string;
  serviceName: string;
  requestNumber: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  submittedAt: string;
  completedAt?: string;
  description?: string;
  fees?: number;
  certificateUrl?: string;
  transactionId?: string;
  paymentStatus?: 'PENDING' | 'SUCCESS' | 'FAILED' | 'PROCESSING';
  paymentDate?: string;
}

const mockServices: Service[] = [
  {
    id: '1',
    name: 'Birth Certificate',
    nameHindi: 'जन्म प्रमाणपत्र',
    description: 'Apply for a new birth certificate or request a duplicate copy',
    descriptionHindi: 'नया जन्म प्रमाणपत्र के लिए आवेदन करें या डुप्लिकेट कॉपी का अनुरोध करें',
    category: 'Civil Registration',
    categoryHindi: 'नागरिक पंजीकरण',
    department: 'Department of Civil Registration',
    departmentHindi: 'नागरिक पंजीकरण विभाग',
    estimatedTime: '7-10 working days',
    estimatedTimeHindi: '7-10 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Hospital Certificate', 'Parent ID Proof'],
    requiredDocumentsHindi: ['आधार कार्ड', 'अस्पताल प्रमाणपत्र', 'माता-पिता की पहचान प्रमाण'],
    fees: 50,
    isActive: true,
  },
  {
    id: '2',
    name: 'Death Certificate',
    nameHindi: 'मृत्यु प्रमाणपत्र',
    description: 'Apply for a death certificate or request a duplicate copy',
    descriptionHindi: 'मृत्यु प्रमाणपत्र के लिए आवेदन करें या डुप्लिकेट कॉपी का अनुरोध करें',
    category: 'Civil Registration',
    categoryHindi: 'नागरिक पंजीकरण',
    department: 'Department of Civil Registration',
    departmentHindi: 'नागरिक पंजीकरण विभाग',
    estimatedTime: '7-10 working days',
    estimatedTimeHindi: '7-10 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Hospital Certificate', 'Applicant ID Proof'],
    requiredDocumentsHindi: ['आधार कार्ड', 'अस्पताल प्रमाणपत्र', 'आवेदक की पहचान प्रमाण'],
    fees: 50,
    isActive: true,
  },
  {
    id: '3',
    name: 'Income Certificate',
    nameHindi: 'आय प्रमाणपत्र',
    description: 'Apply for income certificate required for various government schemes',
    descriptionHindi: 'विभिन्न सरकारी योजनाओं के लिए आवश्यक आय प्रमाणपत्र के लिए आवेदन करें',
    category: 'Certificates',
    categoryHindi: 'प्रमाणपत्र',
    department: 'Revenue Department',
    departmentHindi: 'राजस्व विभाग',
    estimatedTime: '15-20 working days',
    estimatedTimeHindi: '15-20 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Residence Proof', 'Income Proof'],
    requiredDocumentsHindi: ['आधार कार्ड', 'निवास प्रमाण', 'आय प्रमाण'],
    fees: 100,
    isActive: true,
  },
  {
    id: '4',
    name: 'Caste Certificate',
    nameHindi: 'जाति प्रमाणपत्र',
    description: 'Apply for caste certificate for reservation benefits',
    descriptionHindi: 'आरक्षण लाभ के लिए जाति प्रमाणपत्र के लिए आवेदन करें',
    category: 'Certificates',
    categoryHindi: 'प्रमाणपत्र',
    department: 'Revenue Department',
    departmentHindi: 'राजस्व विभाग',
    estimatedTime: '15-20 working days',
    estimatedTimeHindi: '15-20 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Residence Proof', 'Caste Proof'],
    requiredDocumentsHindi: ['आधार कार्ड', 'निवास प्रमाण', 'जाति प्रमाण'],
    fees: 100,
    isActive: true,
  },
  {
    id: '5',
    name: 'Domicile Certificate',
    nameHindi: 'अधिवास प्रमाणपत्र',
    description: 'Apply for domicile certificate for educational and employment purposes',
    descriptionHindi: 'शैक्षिक और रोजगार उद्देश्यों के लिए अधिवास प्रमाणपत्र के लिए आवेदन करें',
    category: 'Certificates',
    categoryHindi: 'प्रमाणपत्र',
    department: 'Revenue Department',
    departmentHindi: 'राजस्व विभाग',
    estimatedTime: '10-15 working days',
    estimatedTimeHindi: '10-15 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Residence Proof', 'Birth Certificate'],
    requiredDocumentsHindi: ['आधार कार्ड', 'निवास प्रमाण', 'जन्म प्रमाणपत्र'],
    fees: 100,
    isActive: true,
  },
  {
    id: '6',
    name: 'Property Registration',
    nameHindi: 'संपत्ति पंजीकरण',
    description: 'Register property transactions and obtain registration certificate',
    descriptionHindi: 'संपत्ति लेनदेन पंजीकृत करें और पंजीकरण प्रमाणपत्र प्राप्त करें',
    category: 'Property Services',
    categoryHindi: 'संपत्ति सेवाएं',
    department: 'Registration Department',
    departmentHindi: 'पंजीकरण विभाग',
    estimatedTime: '30-45 working days',
    estimatedTimeHindi: '30-45 कार्य दिवस',
    requiredDocuments: ['Property Documents', 'ID Proof', 'Payment Receipt'],
    requiredDocumentsHindi: ['संपत्ति दस्तावेज़', 'पहचान प्रमाण', 'भुगतान रसीद'],
    fees: 5000,
    isActive: true,
  },
  {
    id: '7',
    name: 'Driving License',
    nameHindi: 'ड्राइविंग लाइसेंस',
    description: 'Apply for new driving license or renew existing license',
    descriptionHindi: 'नया ड्राइविंग लाइसेंस के लिए आवेदन करें या मौजूदा लाइसेंस नवीनीकृत करें',
    category: 'Transport',
    categoryHindi: 'परिवहन',
    department: 'Transport Department',
    departmentHindi: 'परिवहन विभाग',
    estimatedTime: '15-20 working days',
    estimatedTimeHindi: '15-20 कार्य दिवस',
    requiredDocuments: ['Aadhaar Card', 'Medical Certificate', 'Learner License'],
    requiredDocumentsHindi: ['आधार कार्ड', 'चिकित्सा प्रमाणपत्र', 'लर्नर लाइसेंस'],
    fees: 500,
    isActive: true,
  },
  {
    id: '8',
    name: 'Vehicle Registration',
    nameHindi: 'वाहन पंजीकरण',
    description: 'Register new vehicle or transfer vehicle ownership',
    descriptionHindi: 'नया वाहन पंजीकृत करें या वाहन स्वामित्व स्थानांतरित करें',
    category: 'Transport',
    categoryHindi: 'परिवहन',
    department: 'Transport Department',
    departmentHindi: 'परिवहन विभाग',
    estimatedTime: '10-15 working days',
    estimatedTimeHindi: '10-15 कार्य दिवस',
    requiredDocuments: ['Vehicle Documents', 'ID Proof', 'Insurance'],
    requiredDocumentsHindi: ['वाहन दस्तावेज़', 'पहचान प्रमाण', 'बीमा'],
    fees: 1000,
    isActive: true,
  },
];

export const ServicesPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  // Helper functions to get localized service data
  const getServiceName = (service: Service): string => {
    return i18n.language === 'hi' && service.nameHindi ? service.nameHindi : service.name;
  };

  const getServiceDescription = (service: Service): string => {
    return i18n.language === 'hi' && service.descriptionHindi ? service.descriptionHindi : service.description;
  };

  const getServiceDepartment = (service: Service): string => {
    return i18n.language === 'hi' && service.departmentHindi ? service.departmentHindi : service.department;
  };

  const getServiceEstimatedTime = (service: Service): string => {
    if (!service.estimatedTime) return '';
    return i18n.language === 'hi' && service.estimatedTimeHindi
      ? service.estimatedTimeHindi
      : service.estimatedTime;
  };

  const getServiceCategory = (service: Service): string => {
    return i18n.language === 'hi' && service.categoryHindi ? service.categoryHindi : service.category;
  };

  const getRequiredDocument = (doc: string, index: number, service: Service): string => {
    if (i18n.language === 'hi' && service.requiredDocumentsHindi && service.requiredDocumentsHindi[index]) {
      return service.requiredDocumentsHindi[index];
    }
    return doc;
  };

  // Determine initial tab based on URL path
  const getInitialTab = () => {
    if (location.pathname.includes('/catalog')) return 0;
    if (location.pathname.includes('/status')) return 1;
    return 0; // Default to catalog
  };

  const [tabValue, setTabValue] = useState(getInitialTab()); // 0: Catalog, 1: Status
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [selectedService, setSelectedService] = useState<Service | null>(null);
  const [requestDialogOpen, setRequestDialogOpen] = useState(false);
  const [serviceRequests, setServiceRequests] = useState<ServiceRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [requestFormData, setRequestFormData] = useState({
    serviceId: '',
    description: '',
  });

  const categories = Array.from(new Set(mockServices.map((s) => s.category)));

  useEffect(() => {
    // Load service requests (mock data for now)
    loadServiceRequests();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language]);

  // Redirect /services to /services/catalog
  useEffect(() => {
    if (location.pathname === '/services') {
      navigate('/services/catalog', { replace: true });
    }
  }, [location.pathname, navigate]);

  const loadServiceRequests = () => {
    setLoading(true);
    // Load from localStorage first
    const storedRequests = localStorage.getItem('serviceRequests');
    let requests: ServiceRequest[] = [];
    
    if (storedRequests) {
      try {
        requests = JSON.parse(storedRequests);
      } catch (err) {
        console.error('Failed to parse stored service requests:', err);
      }
    }
    
    // If no stored requests, initialize with default mock data
    if (requests.length === 0) {
      // Get localized service names for mock requests
      const birthCertService = mockServices.find(s => s.id === '1');
      const incomeCertService = mockServices.find(s => s.id === '3');
      
      requests = [
        {
          id: '1',
          serviceId: '1',
          serviceName: birthCertService ? getServiceName(birthCertService) : 'Birth Certificate',
          requestNumber: 'SR-2024-001',
          status: 'COMPLETED',
          submittedAt: '2024-01-15T10:00:00',
          completedAt: '2024-01-22T14:30:00',
          description: 'Request for duplicate birth certificate',
          fees: 50,
          certificateUrl: '/certificates/birth-certificate-sr-2024-001.pdf',
          transactionId: 'TXN-2024-001234',
          paymentStatus: 'SUCCESS',
          paymentDate: '2024-01-15T11:30:00',
        },
        {
          id: '2',
          serviceId: '3',
          serviceName: incomeCertService ? getServiceName(incomeCertService) : 'Income Certificate',
          requestNumber: 'SR-2024-002',
          status: 'IN_PROGRESS',
          submittedAt: '2024-01-20T09:00:00',
          description: 'Required for scholarship application',
          fees: 100,
          transactionId: 'TXN-2024-001567',
          paymentStatus: 'SUCCESS',
          paymentDate: '2024-01-20T10:15:00',
        },
      ];
      // Save initial data to localStorage
      localStorage.setItem('serviceRequests', JSON.stringify(requests));
    }
    
    // Update localized service names for existing requests
    requests = requests.map((req) => {
      const service = mockServices.find(s => s.id === req.serviceId);
      if (service) {
        return {
          ...req,
          serviceName: getServiceName(service),
        };
      }
      return req;
    });
    
    setServiceRequests(requests);
    setLoading(false);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    // Update URL based on tab
    const paths = ['/services/catalog', '/services/status'];
    navigate(paths[newValue], { replace: true });
  };

  // Update tab when URL changes
  useEffect(() => {
    const newTab = (() => {
      if (location.pathname.includes('/catalog')) return 0;
      if (location.pathname.includes('/status')) return 1;
      return 0;
    })();
    if (newTab !== tabValue) {
      setTabValue(newTab);
    }
  }, [location.pathname]);

  const handleServiceClick = (service: Service) => {
    setSelectedService(service);
    setRequestDialogOpen(true);
    setRequestFormData({
      serviceId: service.id,
      description: '',
    });
  };

  const handleRequestSubmit = () => {
    if (!requestFormData.serviceId || !requestFormData.description.trim()) {
      showError(t('services.errors.descriptionRequired', { defaultValue: 'Please provide a description' }));
      return;
    }

    const service = mockServices.find((s) => s.id === requestFormData.serviceId);
    if (!service) {
      showError(t('services.errors.serviceNotFound', { defaultValue: 'Service not found' }));
      return;
    }

    // Simulate API call
    const newRequest: ServiceRequest = {
      id: Date.now().toString(),
      serviceId: requestFormData.serviceId,
      serviceName: getServiceName(service),
      requestNumber: `SR-2024-${String(serviceRequests.length + 1).padStart(3, '0')}`,
      status: 'PENDING',
      submittedAt: new Date().toISOString(),
      description: requestFormData.description,
      fees: service.fees,
    };

    const updatedRequests = [newRequest, ...serviceRequests];
    setServiceRequests(updatedRequests);
    
    // Save to localStorage
    localStorage.setItem('serviceRequests', JSON.stringify(updatedRequests));
    
    setRequestDialogOpen(false);
    setRequestFormData({ serviceId: '', description: '' });
    showSuccess(t('services.requestSubmitted', { defaultValue: 'Service request submitted successfully!' }));
    setTabValue(1); // Switch to Status tab
  };

  const filteredServices = mockServices.filter((service) => {
    const matchesSearch =
      service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      service.department.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !categoryFilter || service.category === categoryFilter;
    return matchesSearch && matchesCategory && service.isActive;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CompletedIcon color="success" />;
      case 'IN_PROGRESS':
        return <PendingIcon color="info" />;
      case 'CANCELLED':
        return <CancelledIcon color="error" />;
      default:
        return <PendingIcon color="warning" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'success';
      case 'IN_PROGRESS':
        return 'info';
      case 'CANCELLED':
        return 'error';
      default:
        return 'warning';
    }
  };

  const getStatusLabel = (status: string): string => {
    return t(`services.status.${status.toLowerCase()}`, { defaultValue: status });
  };

  const getPaymentStatusLabel = (status: string): string => {
    return t(`payments.status.${status.toLowerCase()}`, { defaultValue: status });
  };

  const getPaymentStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    switch (status) {
      case 'SUCCESS':
      case 'COMPLETED':
        return 'success';
      case 'FAILED':
        return 'error';
      case 'PROCESSING':
        return 'info';
      case 'PENDING':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleDownloadCertificate = (request: ServiceRequest) => {
    if (!request.certificateUrl) {
      showError(t('services.noCertificateAvailable', { defaultValue: 'Certificate not available yet' }));
      return;
    }

    try {
      // Simulate certificate download
      // In a real implementation, this would fetch the certificate from the backend
      const link = document.createElement('a');
      link.href = request.certificateUrl;
      link.download = `${request.serviceName}-${request.requestNumber}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showSuccess(t('services.certificateDownloaded', { defaultValue: 'Certificate downloaded successfully' }));
    } catch (error) {
      console.error('Failed to download certificate:', error);
      showError(t('services.certificateDownloadFailed', { defaultValue: 'Failed to download certificate' }));
    }
  };

  const activeRequests = serviceRequests.filter((r) => r.status !== 'COMPLETED' && r.status !== 'CANCELLED');
  const completedRequests = serviceRequests.filter((r) => r.status === 'COMPLETED');

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('services.title', { defaultValue: 'Government Services' })}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        {t('services.subtitle', { defaultValue: 'Browse and request various government services online' })}
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={<ServiceIcon />}
            iconPosition="start"
            label={t('services.catalog', { defaultValue: 'Service Catalog' })}
          />
          <Tab
            icon={<InfoIcon />}
            iconPosition="start"
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('services.statusLabel', { defaultValue: 'Service Status' })}
                {activeRequests.length > 0 && (
                  <Badge badgeContent={activeRequests.length} color="primary">
                    <Box />
                  </Badge>
                )}
              </Box>
            }
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={12} sm={6} md={8}>
                <TextField
                  fullWidth
                  placeholder={t('services.searchPlaceholder', { defaultValue: 'Search services...' })}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                    endAdornment: searchQuery && (
                      <InputAdornment position="end">
                        <IconButton size="small" onClick={() => setSearchQuery('')}>
                          <ClearIcon />
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <FormControl fullWidth>
                  <InputLabel>{t('services.filterByCategory', { defaultValue: 'Category' })}</InputLabel>
                  <Select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    label={t('services.filterByCategory', { defaultValue: 'Category' })}
                    endAdornment={
                      categoryFilter && (
                        <InputAdornment position="end">
                          <IconButton size="small" onClick={() => setCategoryFilter('')}>
                            <ClearIcon />
                          </IconButton>
                        </InputAdornment>
                      )
                    }
                  >
                    <MenuItem value="">{t('common.all', { defaultValue: 'All Categories' })}</MenuItem>
                    {categories.map((category) => {
                      const service = mockServices.find(s => s.category === category);
                      const displayCategory = service ? getServiceCategory(service) : category;
                      return (
                        <MenuItem key={category} value={category}>
                          {displayCategory}
                        </MenuItem>
                      );
                    })}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>

          {filteredServices.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ServiceIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('services.noServicesFound', { defaultValue: 'No services found' })}
              </Typography>
            </Box>
          ) : (
            <Grid container spacing={3}>
              {filteredServices.map((service) => (
                <Grid item xs={12} sm={6} md={4} key={service.id}>
                  <Card
                    sx={{
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      '&:hover': {
                        boxShadow: 4,
                      },
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                        <ServiceIcon color="primary" sx={{ fontSize: 40 }} />
                        <Chip label={getServiceCategory(service)} size="small" color="primary" variant="outlined" />
                      </Box>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {getServiceName(service)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {getServiceDescription(service)}
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="text.secondary" display="block">
                          <strong>{t('services.department', { defaultValue: 'Department' })}:</strong> {getServiceDepartment(service)}
                        </Typography>
                        {service.estimatedTime && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            <strong>{t('services.estimatedTime', { defaultValue: 'Estimated Time' })}:</strong>{' '}
                            {getServiceEstimatedTime(service)}
                          </Typography>
                        )}
                        {service.fees !== undefined && (
                          <Typography variant="caption" color="text.secondary" display="block">
                            <strong>{t('services.fees', { defaultValue: 'Fees' })}:</strong> ₹{service.fees}
                          </Typography>
                        )}
                      </Box>
                    </CardContent>
                    <CardActions sx={{ flexDirection: 'column', gap: 1, p: 2 }}>
                      <Button
                        size="small"
                        variant="contained"
                        fullWidth
                        endIcon={<ArrowForwardIcon />}
                        onClick={() => handleServiceClick(service)}
                      >
                        {t('services.request', { defaultValue: 'Request Service' })}
                      </Button>
                      {service.fees !== undefined && service.fees > 0 && (
                        <Button
                          size="small"
                          variant="outlined"
                          fullWidth
                          startIcon={<PaymentIcon />}
                          onClick={() => navigate(`/payments?serviceRequestId=${service.id}&amount=${service.fees}`)}
                        >
                          {t('services.makePayment', { defaultValue: 'Make Payment' })}
                        </Button>
                      )}
                      {service.requiredDocuments && service.requiredDocuments.length > 0 && (
                        <Button
                          size="small"
                          variant="outlined"
                          fullWidth
                          startIcon={<DocumentIcon />}
                          onClick={() => navigate(`/documents?serviceId=${service.id}`)}
                        >
                          {t('services.viewDocuments', { defaultValue: 'View Documents' })}
                        </Button>
                      )}
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : serviceRequests.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <InfoIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('services.noRequests', { defaultValue: 'No service requests found' })}
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setTabValue(0)}
                sx={{ mt: 2 }}
              >
                {t('services.requestNewService', { defaultValue: 'Request a Service' })}
              </Button>
            </Box>
          ) : (
            <Box>
              {activeRequests.length > 0 && (
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    {t('services.activeRequests', { defaultValue: 'Active Requests' })}
                  </Typography>
                  <List>
                    {activeRequests.map((request) => (
                      <Paper key={request.id} variant="outlined" sx={{ mb: 2 }}>
                        <ListItem>
                          <ListItemIcon>{getStatusIcon(request.status)}</ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">{request.serviceName}</Typography>
                                <Chip
                                  label={getStatusLabel(request.status, i18n.language)}
                                  size="small"
                                  color={getStatusColor(request.status) as any}
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {t('services.requestNumber', { defaultValue: 'Request Number' })}: {request.requestNumber}
                                </Typography>
                                {request.description && (
                                  <Typography variant="body2" color="text.secondary">
                                    {request.description}
                                  </Typography>
                                )}
                                <Typography variant="caption" color="text.secondary">
                                  {t('services.submittedOn', { defaultValue: 'Submitted on' })}: {formatDate(request.submittedAt)}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                        {request.transactionId && (
                          <Box sx={{ px: 2, pb: 2 }}>
                            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <PaymentIcon fontSize="small" color="primary" />
                                {t('services.paymentInfo', { defaultValue: 'Payment Information' })}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                  <strong>{t('services.transactionId', { defaultValue: 'Transaction ID' })}:</strong>{' '}
                                  <Typography component="span" sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                                    {request.transactionId}
                                  </Typography>
                                </Typography>
                                {request.paymentStatus && (
                                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    <strong>{t('services.paymentStatus', { defaultValue: 'Payment Status' })}:</strong>{' '}
                                    <Chip
                                      label={getPaymentStatusLabel(request.paymentStatus)}
                                      size="small"
                                      color={getPaymentStatusColor(request.paymentStatus)}
                                      sx={{ ml: 1 }}
                                    />
                                  </Typography>
                                )}
                                {request.paymentDate && (
                                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                    {t('services.paidOn', { defaultValue: 'Paid on' })}: {formatDate(request.paymentDate)}
                                  </Typography>
                                )}
                              </Box>
                            </Paper>
                          </Box>
                        )}
                      </Paper>
                    ))}
                  </List>
                </Box>
              )}

              {completedRequests.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {t('services.completedRequests', { defaultValue: 'Completed Requests' })}
                  </Typography>
                  <List>
                    {completedRequests.map((request) => (
                      <Paper key={request.id} variant="outlined" sx={{ mb: 2 }}>
                        <ListItem
                          secondaryAction={
                            request.certificateUrl ? (
                              <IconButton
                                edge="end"
                                aria-label={t('services.downloadCertificate', { defaultValue: 'Download Certificate' })}
                                onClick={() => handleDownloadCertificate(request)}
                              >
                                <DownloadIcon />
                              </IconButton>
                            ) : null
                          }
                        >
                          <ListItemIcon>{getStatusIcon(request.status)}</ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="subtitle1">{request.serviceName}</Typography>
                                <Chip
                                  label={getStatusLabel(request.status, i18n.language)}
                                  size="small"
                                  color={getStatusColor(request.status) as any}
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {t('services.requestNumber', { defaultValue: 'Request Number' })}: {request.requestNumber}
                                </Typography>
                                {request.completedAt && (
                                  <Typography variant="caption" color="text.secondary">
                                    {t('services.completedOn', { defaultValue: 'Completed on' })}: {formatDate(request.completedAt)}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                        {request.transactionId && (
                          <Box sx={{ px: 2, pb: 2 }}>
                            <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                              <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <PaymentIcon fontSize="small" color="primary" />
                                {t('services.paymentInfo', { defaultValue: 'Payment Information' })}
                              </Typography>
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="body2" color="text.secondary">
                                  <strong>{t('services.transactionId', { defaultValue: 'Transaction ID' })}:</strong>{' '}
                                  <Typography component="span" sx={{ fontFamily: 'monospace', fontWeight: 'bold' }}>
                                    {request.transactionId}
                                  </Typography>
                                </Typography>
                                {request.paymentStatus && (
                                  <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                    <strong>{t('services.paymentStatus', { defaultValue: 'Payment Status' })}:</strong>{' '}
                                    <Chip
                                      label={getPaymentStatusLabel(request.paymentStatus)}
                                      size="small"
                                      color={getPaymentStatusColor(request.paymentStatus)}
                                      sx={{ ml: 1 }}
                                    />
                                  </Typography>
                                )}
                                {request.paymentDate && (
                                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 0.5 }}>
                                    {t('services.paidOn', { defaultValue: 'Paid on' })}: {formatDate(request.paymentDate)}
                                  </Typography>
                                )}
                              </Box>
                            </Paper>
                          </Box>
                        )}
                      </Paper>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </TabPanel>
      </Paper>

      {/* Request Service Dialog */}
      <Dialog open={requestDialogOpen} onClose={() => setRequestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {t('services.requestService', { defaultValue: 'Request Service' })}
          {selectedService && `: ${getServiceName(selectedService)}`}
        </DialogTitle>
        <DialogContent>
          {selectedService && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  {t('services.serviceDetails', { defaultValue: 'Service Details' })}
                </Typography>
                <Typography variant="body2">
                  <strong>{t('services.department', { defaultValue: 'Department' })}:</strong> {getServiceDepartment(selectedService)}
                </Typography>
                {selectedService.estimatedTime && (
                  <Typography variant="body2">
                    <strong>{t('services.estimatedTime', { defaultValue: 'Estimated Time' })}:</strong>{' '}
                    {getServiceEstimatedTime(selectedService)}
                  </Typography>
                )}
                {selectedService.fees !== undefined && (
                  <Typography variant="body2">
                    <strong>{t('services.fees', { defaultValue: 'Fees' })}:</strong> ₹{selectedService.fees}
                  </Typography>
                )}
                {selectedService.requiredDocuments && selectedService.requiredDocuments.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2">
                        <strong>{t('services.requiredDocuments', { defaultValue: 'Required Documents' })}:</strong>
                      </Typography>
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<DocumentIcon />}
                        onClick={() => {
                          setRequestDialogOpen(false);
                          navigate(`/documents?serviceId=${selectedService.id}`);
                        }}
                      >
                        {t('services.uploadDocuments', { defaultValue: 'Upload Documents' })}
                      </Button>
                    </Box>
                    <List dense>
                      {selectedService.requiredDocuments.map((doc, index) => (
                        <ListItem key={index} sx={{ py: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <ArrowForwardIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary={getRequiredDocument(doc, index, selectedService)} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Alert>
              <Divider sx={{ my: 2 }} />
              <TextField
                fullWidth
                multiline
                rows={4}
                label={t('services.description', { defaultValue: 'Description / Additional Information' })}
                value={requestFormData.description}
                onChange={(e) => setRequestFormData((prev) => ({ ...prev, description: e.target.value }))}
                placeholder={t('services.descriptionPlaceholder', {
                  defaultValue: 'Please provide any additional information or requirements...',
                })}
                required
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRequestDialogOpen(false)}>
            {t('common.cancel', { defaultValue: 'Cancel' })}
          </Button>
          {selectedService && selectedService.fees !== undefined && selectedService.fees > 0 && (
            <Button
              variant="outlined"
              startIcon={<PaymentIcon />}
              onClick={() => {
                setRequestDialogOpen(false);
                navigate(`/payments?serviceRequestId=${selectedService.id}&amount=${selectedService.fees}&serviceName=${encodeURIComponent(getServiceName(selectedService))}`);
              }}
            >
              {t('services.makePayment', { defaultValue: 'Make Payment' })}
            </Button>
          )}
          <Button
            variant="contained"
            onClick={handleRequestSubmit}
            disabled={!requestFormData.description.trim()}
          >
            {t('services.submitRequest', { defaultValue: 'Submit Request' })}
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

