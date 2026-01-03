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
  TextField,
  InputAdornment,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Alert,
  Divider,
  CircularProgress,
  Badge,
} from '@mui/material';
import {
  Search as SearchIcon,
  Help as HelpIcon,
  QuestionAnswer as FAQIcon,
  ContactSupport as ContactIcon,
  Add as AddIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as ResolvedIcon,
  HourglassEmpty as PendingIcon,
  Cancel as CancelledIcon,
  Assignment as InProgressIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  LocationOn as LocationIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { getTicketStatusLabel, getTicketPriorityLabel, getTicketCategoryLabel, getFAQCategoryLabel } from '@/utils/localization';

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
      id={`help-tabpanel-${index}`}
      aria-labelledby={`help-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface FAQ {
  id: string;
  question: string;
  questionHindi: string;
  answer: string;
  answerHindi: string;
  category: string;
}

interface Ticket {
  id: string;
  ticketNumber: string;
  subject: string;
  description: string;
  category: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'RESOLVED' | 'CLOSED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';
  createdAt: string;
  updatedAt: string;
  resolvedAt?: string;
  resolution?: string;
}

const mockFAQs: FAQ[] = [
  {
    id: '1',
    question: 'How do I apply for a government scheme?',
    questionHindi: 'मैं सरकारी योजना के लिए कैसे आवेदन करूं?',
    answer: 'You can browse available schemes from the Schemes menu, check your eligibility using the Eligibility Checker, and then submit an application. Make sure you have all required documents ready before applying.',
    answerHindi: 'आप योजनाएं मेनू से उपलब्ध योजनाओं को ब्राउज़ कर सकते हैं, पात्रता जांचकर्ता का उपयोग करके अपनी पात्रता की जांच कर सकते हैं, और फिर एक आवेदन सबमिट कर सकते हैं। आवेदन करने से पहले सुनिश्चित करें कि आपके पास सभी आवश्यक दस्तावेज़ तैयार हैं।',
    category: 'Applications',
  },
  {
    id: '2',
    question: 'What documents are required for scheme applications?',
    questionHindi: 'योजना आवेदन के लिए कौन से दस्तावेज़ आवश्यक हैं?',
    answer: 'Required documents vary by scheme. Generally, you will need Aadhaar card, proof of residence, income certificate, and scheme-specific documents. Check the scheme details page for the complete list.',
    answerHindi: 'आवश्यक दस्तावेज़ योजना के अनुसार भिन्न होते हैं। आम तौर पर, आपको आधार कार्ड, निवास प्रमाण, आय प्रमाणपत्र, और योजना-विशिष्ट दस्तावेज़ों की आवश्यकता होगी। पूरी सूची के लिए योजना विवरण पृष्ठ देखें।',
    category: 'Applications',
  },
  {
    id: '3',
    question: 'How can I track my application status?',
    questionHindi: 'मैं अपने आवेदन की स्थिति कैसे ट्रैक कर सकता हूं?',
    answer: 'You can track your application status from the "My Applications" page. You will also receive notifications when your application status changes.',
    answerHindi: 'आप "मेरे आवेदन" पृष्ठ से अपने आवेदन की स्थिति ट्रैक कर सकते हैं। जब आपके आवेदन की स्थिति बदलती है तो आपको सूचनाएं भी मिलेंगी।',
    category: 'Applications',
  },
  {
    id: '4',
    question: 'How do I upload documents?',
    questionHindi: 'मैं दस्तावेज़ कैसे अपलोड करूं?',
    answer: 'Go to the Documents page, click on "Upload Document", select the document type, choose the file, and click Upload. Make sure the file is in PDF, JPG, or PNG format and under 5MB.',
    answerHindi: 'दस्तावेज़ पृष्ठ पर जाएं, "दस्तावेज़ अपलोड करें" पर क्लिक करें, दस्तावेज़ प्रकार चुनें, फ़ाइल चुनें, और अपलोड पर क्लिक करें। सुनिश्चित करें कि फ़ाइल PDF, JPG, या PNG प्रारूप में है और 5MB से कम है।',
    category: 'Documents',
  },
  {
    id: '5',
    question: 'What should I do if my document is rejected?',
    questionHindi: 'यदि मेरा दस्तावेज़ अस्वीकृत हो जाए तो मुझे क्या करना चाहिए?',
    answer: 'If your document is rejected, you will receive a notification with the reason. You can upload a new document with the corrections. Check the verification notes for specific requirements.',
    answerHindi: 'यदि आपका दस्तावेज़ अस्वीकृत हो जाता है, तो आपको कारण के साथ एक सूचना मिलेगी। आप सुधार के साथ एक नया दस्तावेज़ अपलोड कर सकते हैं। विशिष्ट आवश्यकताओं के लिए सत्यापन नोट्स देखें।',
    category: 'Documents',
  },
  {
    id: '6',
    question: 'How do I check my benefit payments?',
    questionHindi: 'मैं अपने लाभ भुगतान कैसे जांचूं?',
    answer: 'Go to the Benefits page to view your current benefits, payment history, and forecast. You can see all transactions and download receipts from there.',
    answerHindi: 'अपने वर्तमान लाभ, भुगतान इतिहास, और पूर्वानुमान देखने के लिए लाभ पृष्ठ पर जाएं। आप वहां से सभी लेनदेन देख सकते हैं और रसीदें डाउनलोड कर सकते हैं।',
    category: 'Benefits',
  },
  {
    id: '7',
    question: 'Can I update my profile information?',
    questionHindi: 'क्या मैं अपनी प्रोफ़ाइल जानकारी अपडेट कर सकता हूं?',
    answer: 'Yes, you can update your profile from the Profile page. Some information like Aadhaar number cannot be changed. Changes may require verification.',
    answerHindi: 'हां, आप प्रोफ़ाइल पृष्ठ से अपनी प्रोफ़ाइल अपडेट कर सकते हैं। कुछ जानकारी जैसे आधार नंबर नहीं बदला जा सकता। परिवर्तन के लिए सत्यापन की आवश्यकता हो सकती है।',
    category: 'Profile',
  },
  {
    id: '8',
    question: 'How do I change my notification preferences?',
    questionHindi: 'मैं अपनी सूचना प्राथमिकताएं कैसे बदलूं?',
    answer: 'Go to Settings > Notification Preferences to manage your notification settings, including email, SMS, and in-app notifications.',
    answerHindi: 'अपनी सूचना सेटिंग्स प्रबंधित करने के लिए सेटिंग्स > सूचना प्राथमिकताएं पर जाएं, जिसमें ईमेल, SMS, और इन-ऐप सूचनाएं शामिल हैं।',
    category: 'Settings',
  },
  {
    id: '9',
    question: 'What should I do if I forget my login credentials?',
    questionHindi: 'यदि मैं अपने लॉगिन क्रेडेंशियल भूल जाऊं तो मुझे क्या करना चाहिए?',
    answer: 'Use the "Forgot Jan Aadhaar" option on the login page. You can also contact support through the Help & Support section.',
    answerHindi: 'लॉगिन पृष्ठ पर "जन आधार भूल गए" विकल्प का उपयोग करें। आप सहायता और समर्थन अनुभाग के माध्यम से सहायता से भी संपर्क कर सकते हैं।',
    category: 'Authentication',
  },
  {
    id: '10',
    question: 'How long does it take to process an application?',
    questionHindi: 'एक आवेदन को संसाधित करने में कितना समय लगता है?',
    answer: 'Processing time varies by scheme and application type. Generally, it takes 15-30 working days. You can check the estimated time on the scheme details page.',
    answerHindi: 'संसाधन समय योजना और आवेदन प्रकार के अनुसार भिन्न होता है। आम तौर पर, इसमें 15-30 कार्य दिवस लगते हैं। आप योजना विवरण पृष्ठ पर अनुमानित समय जांच सकते हैं।',
    category: 'Applications',
  },
];

export const HelpPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  // Helper functions to get localized FAQ content
  const getFAQQuestion = (faq: FAQ): string => {
    return i18n.language === 'hi' && faq.questionHindi ? faq.questionHindi : faq.question;
  };

  const getFAQAnswer = (faq: FAQ): string => {
    return i18n.language === 'hi' && faq.answerHindi ? faq.answerHindi : faq.answer;
  };

  const [tabValue, setTabValue] = useState(0); // 0: Help Hub, 1: My Tickets
  const [searchQuery, setSearchQuery] = useState('');
  const [faqCategory, setFaqCategory] = useState('');
  const [expandedFAQ, setExpandedFAQ] = useState<string | false>(false);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [loading, setLoading] = useState(false);
  const [ticketDialogOpen, setTicketDialogOpen] = useState(false);
  const [ticketFormData, setTicketFormData] = useState({
    subject: '',
    description: '',
    category: '',
    priority: 'MEDIUM',
  });

  const faqCategories = Array.from(new Set(mockFAQs.map((faq) => faq.category)));

  // Load tickets from localStorage on component mount
  useEffect(() => {
    loadTickets();
  }, []);

  useEffect(() => {
    if (tabValue === 1) {
      loadTickets();
    }
  }, [tabValue]);

  const loadTickets = () => {
    setLoading(true);
    // Load tickets from localStorage
    const savedTickets = localStorage.getItem('helpTickets');
    let ticketsFromStorage: Ticket[] = [];
    
    if (savedTickets) {
      try {
        ticketsFromStorage = JSON.parse(savedTickets);
      } catch (error) {
        console.error('Error parsing tickets from localStorage:', error);
      }
    }

    // Load mock tickets (for initial demo data)
    const mockTickets: Ticket[] = [
      {
        id: '1',
        ticketNumber: 'TKT-2024-001',
        subject: 'Unable to upload document',
        description: 'I am unable to upload my Aadhaar card. The upload button is not working.',
        category: 'Technical Issue',
        status: 'IN_PROGRESS',
        priority: 'HIGH',
        createdAt: '2024-01-18T10:00:00',
        updatedAt: '2024-01-19T14:30:00',
      },
      {
        id: '2',
        ticketNumber: 'TKT-2024-002',
        subject: 'Application status not updating',
        description: 'My application status has been showing as "Under Review" for the past 3 weeks.',
        category: 'Application Inquiry',
        status: 'RESOLVED',
        priority: 'MEDIUM',
        createdAt: '2024-01-10T09:00:00',
        updatedAt: '2024-01-15T16:00:00',
        resolvedAt: '2024-01-15T16:00:00',
        resolution: 'Your application has been processed and approved. You will receive the benefits shortly.',
      },
    ];

    // Merge: prioritize saved tickets, but include mock tickets that don't exist in saved tickets
    const existingIds = new Set(ticketsFromStorage.map(t => t.id));
    const uniqueMockTickets = mockTickets.filter(t => !existingIds.has(t.id));
    const allTickets = [...ticketsFromStorage, ...uniqueMockTickets];
    
    // Sort by creation date (newest first)
    allTickets.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
    
    setTickets(allTickets);
    setLoading(false);
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFAQChange = (panel: string) => (_event: React.SyntheticEvent, isExpanded: boolean) => {
    setExpandedFAQ(isExpanded ? panel : false);
  };

  const handleCreateTicket = () => {
    if (!ticketFormData.subject.trim() || !ticketFormData.description.trim() || !ticketFormData.category) {
      showError(t('help.errors.fillAllFields', { defaultValue: 'Please fill all required fields' }));
      return;
    }

    // Generate ticket number based on current year and total tickets count
    const currentYear = new Date().getFullYear();
    const savedTickets = localStorage.getItem('helpTickets');
    let existingTickets: Ticket[] = [];
    if (savedTickets) {
      try {
        existingTickets = JSON.parse(savedTickets);
      } catch (error) {
        console.error('Error parsing tickets from localStorage:', error);
      }
    }
    const ticketCount = existingTickets.length + tickets.filter(t => !existingTickets.some(et => et.id === t.id)).length;
    
    const newTicket: Ticket = {
      id: Date.now().toString(),
      ticketNumber: `TKT-${currentYear}-${String(ticketCount + 1).padStart(3, '0')}`,
      subject: ticketFormData.subject,
      description: ticketFormData.description,
      category: ticketFormData.category,
      status: 'OPEN',
      priority: ticketFormData.priority as any,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    // Update state
    const updatedTickets = [newTicket, ...tickets];
    setTickets(updatedTickets);
    
    // Save to localStorage
    const ticketsToSave = updatedTickets.filter(t => !['1', '2'].includes(t.id)); // Exclude mock tickets
    localStorage.setItem('helpTickets', JSON.stringify(ticketsToSave));
    
    setTicketDialogOpen(false);
    setTicketFormData({ subject: '', description: '', category: '', priority: 'MEDIUM' });
    showSuccess(t('help.ticketCreated', { defaultValue: 'Support ticket created successfully!' }));
  };

  const filteredFAQs = mockFAQs.filter((faq) => {
    const matchesSearch =
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = !faqCategory || faq.category === faqCategory;
    return matchesSearch && matchesCategory;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return <ResolvedIcon color="success" fontSize="small" />;
      case 'IN_PROGRESS':
        return <InProgressIcon color="info" fontSize="small" />;
      case 'CLOSED':
        return <CancelledIcon color="default" fontSize="small" />;
      default:
        return <PendingIcon color="warning" fontSize="small" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'error';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'info';
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

  const openTickets = tickets.filter((t) => t.status !== 'RESOLVED' && t.status !== 'CLOSED');
  const resolvedTickets = tickets.filter((t) => t.status === 'RESOLVED' || t.status === 'CLOSED');

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
        {t('help.title', { defaultValue: 'Help & Support' })}
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        {t('help.subtitle', { defaultValue: 'Find answers to common questions or get support from our team' })}
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab
            icon={<HelpIcon />}
            iconPosition="start"
            label={t('help.helpHub', { defaultValue: 'Help Hub' })}
          />
          <Tab
            icon={<ContactIcon />}
            iconPosition="start"
            label={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                {t('help.myTickets', { defaultValue: 'My Tickets' })}
                {openTickets.length > 0 && (
                  <Badge badgeContent={openTickets.length} color="primary">
                    <Box />
                  </Badge>
                )}
              </Box>
            }
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            {/* Search and Filter */}
            <Grid item xs={12}>
              <Box sx={{ mb: 3 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={8}>
                    <TextField
                      fullWidth
                      placeholder={t('help.searchFAQs', { defaultValue: 'Search FAQs...' })}
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
                  <Grid item xs={12} sm={4}>
                    <FormControl fullWidth>
                      <InputLabel>{t('help.category', { defaultValue: 'Category' })}</InputLabel>
                      <Select
                        value={faqCategory}
                        onChange={(e) => setFaqCategory(e.target.value)}
                        label={t('help.category', { defaultValue: 'Category' })}
                      >
                        <MenuItem value="">{t('common.all', { defaultValue: 'All Categories' })}</MenuItem>
                        {faqCategories.map((category) => (
                          <MenuItem key={category} value={category}>
                            {getFAQCategoryLabel(category, t)}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>
            </Grid>

            {/* FAQs */}
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <FAQIcon color="primary" />
                <Typography variant="h6">
                  {t('help.frequentlyAskedQuestions', { defaultValue: 'Frequently Asked Questions' })}
                </Typography>
              </Box>
              {filteredFAQs.length === 0 ? (
                <Alert severity="info">
                  {t('help.noFAQsFound', { defaultValue: 'No FAQs found matching your search criteria.' })}
                </Alert>
              ) : (
                <Box>
                  {filteredFAQs.map((faq) => (
                    <Accordion
                      key={faq.id}
                      expanded={expandedFAQ === faq.id}
                      onChange={handleFAQChange(faq.id)}
                    >
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                          <Typography variant="subtitle1" sx={{ flexGrow: 1 }}>
                            {getFAQQuestion(faq)}
                          </Typography>
                          <Chip label={getFAQCategoryLabel(faq.category, t)} size="small" variant="outlined" />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
                          {getFAQAnswer(faq)}
                        </Typography>
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </Box>
              )}
            </Grid>

            {/* Contact Options */}
            <Grid item xs={12}>
              <Card variant="outlined">
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <ContactIcon color="primary" />
                    <Typography variant="h6">
                      {t('help.contactSupport', { defaultValue: 'Contact Support' })}
                    </Typography>
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <PhoneIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          {t('help.phone', { defaultValue: 'Phone' })}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          1800-XXX-XXXX
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {t('help.phoneHours', { defaultValue: 'Mon-Sat, 9 AM - 6 PM' })}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <EmailIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          {t('help.email', { defaultValue: 'Email' })}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          support@smart.gov.in
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {t('help.emailResponse', { defaultValue: 'Response within 24 hours' })}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Box sx={{ textAlign: 'center', p: 2 }}>
                        <LocationIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                        <Typography variant="subtitle2" gutterBottom>
                          {t('help.office', { defaultValue: 'Office' })}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {t('help.officeAddress', { defaultValue: 'SMART Portal Office, Jaipur' })}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          {t('help.officeHours', { defaultValue: 'Mon-Fri, 10 AM - 5 PM' })}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      startIcon={<AddIcon />}
                      onClick={() => setTicketDialogOpen(true)}
                      size="large"
                    >
                      {t('help.createTicket', { defaultValue: 'Create Support Ticket' })}
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          {!isAuthenticated ? (
            <Alert severity="warning">
              {t('help.loginRequired', { defaultValue: 'Please log in to view your support tickets.' })}
            </Alert>
          ) : loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : tickets.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ContactIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                {t('help.noTickets', { defaultValue: 'No support tickets found' })}
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setTicketDialogOpen(true)}
                sx={{ mt: 2 }}
              >
                {t('help.createTicket', { defaultValue: 'Create Support Ticket' })}
              </Button>
            </Box>
          ) : (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6">
                  {t('help.myTickets', { defaultValue: 'My Tickets' })}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setTicketDialogOpen(true)}
                >
                  {t('help.createTicket', { defaultValue: 'Create Ticket' })}
                </Button>
              </Box>

              {openTickets.length > 0 && (
                <Box sx={{ mb: 4 }}>
                  <Typography variant="h6" gutterBottom>
                    {t('help.openTickets', { defaultValue: 'Open Tickets' })}
                  </Typography>
                  <List>
                    {openTickets.map((ticket) => (
                      <Paper key={ticket.id} variant="outlined" sx={{ mb: 2 }}>
                        <ListItem>
                          <ListItemIcon>{getStatusIcon(ticket.status)}</ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                <Typography variant="subtitle1">{ticket.subject}</Typography>
                                <Chip
                                  label={getTicketStatusLabel(ticket.status, t)}
                                  size="small"
                                  color={getStatusColor(ticket.status) as any}
                                />
                                <Chip
                                  label={getTicketPriorityLabel(ticket.priority, t)}
                                  size="small"
                                  color={getPriorityColor(ticket.priority) as any}
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {t('help.ticketNumber', { defaultValue: 'Ticket Number' })}: {ticket.ticketNumber}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {ticket.description}
                                </Typography>
                                <Typography variant="caption" color="text.secondary">
                                  {t('help.createdOn', { defaultValue: 'Created on' })}: {formatDate(ticket.createdAt)}
                                </Typography>
                              </Box>
                            }
                          />
                        </ListItem>
                      </Paper>
                    ))}
                  </List>
                </Box>
              )}

              {resolvedTickets.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    {t('help.resolvedTickets', { defaultValue: 'Resolved Tickets' })}
                  </Typography>
                  <List>
                    {resolvedTickets.map((ticket) => (
                      <Paper key={ticket.id} variant="outlined" sx={{ mb: 2 }}>
                        <ListItem>
                          <ListItemIcon>{getStatusIcon(ticket.status)}</ListItemIcon>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                                <Typography variant="subtitle1">{ticket.subject}</Typography>
                                <Chip
                                  label={getTicketStatusLabel(ticket.status, t)}
                                  size="small"
                                  color={getStatusColor(ticket.status) as any}
                                />
                              </Box>
                            }
                            secondary={
                              <Box>
                                <Typography variant="body2" color="text.secondary">
                                  {t('help.ticketNumber', { defaultValue: 'Ticket Number' })}: {ticket.ticketNumber}
                                </Typography>
                                {ticket.resolution && (
                                  <Alert severity="success" sx={{ mt: 1, mb: 1 }}>
                                    <Typography variant="body2">
                                      <strong>{t('help.resolution', { defaultValue: 'Resolution' })}:</strong>{' '}
                                      {ticket.resolution}
                                    </Typography>
                                  </Alert>
                                )}
                                {ticket.resolvedAt && (
                                  <Typography variant="caption" color="text.secondary">
                                    {t('help.resolvedOn', { defaultValue: 'Resolved on' })}: {formatDate(ticket.resolvedAt)}
                                  </Typography>
                                )}
                              </Box>
                            }
                          />
                        </ListItem>
                      </Paper>
                    ))}
                  </List>
                </Box>
              )}
            </Box>
          )}
        </TabPanel>
      </Paper>

      {/* Create Ticket Dialog */}
      <Dialog open={ticketDialogOpen} onClose={() => setTicketDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>{t('help.createTicket', { defaultValue: 'Create Support Ticket' })}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label={t('help.subject', { defaultValue: 'Subject' })}
                value={ticketFormData.subject}
                onChange={(e) => setTicketFormData((prev) => ({ ...prev, subject: e.target.value }))}
                required
                placeholder={t('help.subjectPlaceholder', { defaultValue: 'Brief description of your issue' })}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>{t('help.category', { defaultValue: 'Category' })}</InputLabel>
                <Select
                  value={ticketFormData.category}
                  onChange={(e) => setTicketFormData((prev) => ({ ...prev, category: e.target.value }))}
                  label={t('help.category', { defaultValue: 'Category' })}
                >
                  <MenuItem value="Technical Issue">
                    {t('help.category.technical', { defaultValue: 'Technical Issue' })}
                  </MenuItem>
                  <MenuItem value="Application Inquiry">
                    {t('help.category.application', { defaultValue: 'Application Inquiry' })}
                  </MenuItem>
                  <MenuItem value="Document Issue">
                    {t('help.category.document', { defaultValue: 'Document Issue' })}
                  </MenuItem>
                  <MenuItem value="Payment Issue">
                    {t('help.category.payment', { defaultValue: 'Payment Issue' })}
                  </MenuItem>
                  <MenuItem value="Account Issue">
                    {t('help.category.account', { defaultValue: 'Account Issue' })}
                  </MenuItem>
                  <MenuItem value="Other">
                    {t('help.category.other', { defaultValue: 'Other' })}
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('help.priority', { defaultValue: 'Priority' })}</InputLabel>
                <Select
                  value={ticketFormData.priority}
                  onChange={(e) => setTicketFormData((prev) => ({ ...prev, priority: e.target.value }))}
                  label={t('help.priority', { defaultValue: 'Priority' })}
                >
                  <MenuItem value="LOW">{t('help.priority.low', { defaultValue: 'Low' })}</MenuItem>
                  <MenuItem value="MEDIUM">{t('help.priority.medium', { defaultValue: 'Medium' })}</MenuItem>
                  <MenuItem value="HIGH">{t('help.priority.high', { defaultValue: 'High' })}</MenuItem>
                  <MenuItem value="URGENT">{t('help.priority.urgent', { defaultValue: 'Urgent' })}</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={6}
                label={t('help.description', { defaultValue: 'Description' })}
                value={ticketFormData.description}
                onChange={(e) => setTicketFormData((prev) => ({ ...prev, description: e.target.value }))}
                required
                placeholder={t('help.descriptionPlaceholder', {
                  defaultValue: 'Please provide detailed information about your issue...',
                })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTicketDialogOpen(false)}>
            {t('common.cancel', { defaultValue: 'Cancel' })}
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateTicket}
            disabled={!ticketFormData.subject.trim() || !ticketFormData.description.trim() || !ticketFormData.category}
          >
            {t('help.submitTicket', { defaultValue: 'Submit Ticket' })}
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

