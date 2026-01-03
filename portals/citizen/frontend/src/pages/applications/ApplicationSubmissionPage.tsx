import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getSchemeName } from '@/utils/localization';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  TextField,
  Stepper,
  Step,
  StepLabel,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  SelectChangeEvent,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { useAppSelector } from '@/store/hooks';
import { schemeService, applicationService, documentService } from '@/services';
import { Scheme, ServiceApplicationRequest, Document } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { DocumentUpload } from '@/components/documents/DocumentUpload';
import { isValidUUID } from '@/utils/uuidValidator';

// Steps will be translated in the component

export const ApplicationSubmissionPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { schemeId } = useParams<{ schemeId: string }>();
  const [searchParams] = useSearchParams();
  const schemeIdFromQuery = searchParams.get('schemeId');

  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scheme, setScheme] = useState<Scheme | null>(null);
  const [uploadedDocuments, setUploadedDocuments] = useState<Document[]>([]);
  const [hasDepartmentQuery, setHasDepartmentQuery] = useState(false); // Track if department has raised a query

  // Form state
  const [formData, setFormData] = useState<ServiceApplicationRequest>({
    schemeId: schemeId || schemeIdFromQuery || undefined,
    serviceType: '',
    applicationType: '',
    subject: '',
    description: '',
    priority: 'NORMAL',
    expectedCompletionDate: '',
    applicationData: {},
  });

  // Service Type options with translations
  const serviceTypes = [
    { value: 'Scheme Application', key: 'schemeApplication' },
    { value: 'Benefit Claim', key: 'benefitClaim' },
    { value: 'Document Verification', key: 'documentVerification' },
    { value: 'Status Inquiry', key: 'statusInquiry' },
    { value: 'Complaint/Feedback', key: 'complaintFeedback' },
    { value: 'Other', key: 'other' },
  ];

  // Application Type options with translations
  const applicationTypes = [
    { value: 'New', key: 'new' },
    { value: 'Renewal', key: 'renewal' },
    { value: 'Modification', key: 'modification' },
    { value: 'Correction', key: 'correction' },
    { value: 'Transfer', key: 'transfer' },
    { value: 'Cancellation', key: 'cancellation' },
  ];

  const finalSchemeId = schemeId || schemeIdFromQuery;

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!user?.id || !isValidUUID(user.id)) {
      setError('Please complete your profile before submitting an application.');
      setLoading(false);
      return;
    }

    if (finalSchemeId) {
      loadSchemeDetails();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user?.id, finalSchemeId, navigate]);

  const loadSchemeDetails = async () => {
    if (!finalSchemeId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await schemeService.getSchemeById(finalSchemeId);
      setScheme(data);
      // Pre-fill service type with scheme name
      setFormData((prev) => ({
        ...prev,
        serviceType: data.name || '',
        schemeId: finalSchemeId,
      }));
    } catch (err: any) {
      console.error('Error loading scheme details:', err);
      const errorMessage = t('application.submit.errors.loadFailed', { defaultValue: 'Failed to load scheme details' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    // Validate current step
    if (activeStep === 0) {
      if (!formData.serviceType?.trim()) {
        const errorMessage = t('application.submit.errors.serviceTypeRequired', { defaultValue: 'Please select service type' });
        setError(errorMessage);
        showError(errorMessage);
        return;
      }
    }

    setError(null);
    
    // Skip Additional Information step (step 2) if no department query
    if (activeStep === 1 && !hasDepartmentQuery) {
      setActiveStep(3); // Skip to Review & Submit (step 3)
    } else {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setError(null);
    // Skip Additional Information step if no department query when going back
    if (activeStep === 3 && !hasDepartmentQuery) {
      setActiveStep(1); // Go back to Documents (skip step 2)
    } else if (activeStep === 2 && !hasDepartmentQuery) {
      setActiveStep(1); // Go back to Documents
    } else {
      setActiveStep((prevStep) => prevStep - 1);
    }
  };

  const handleDocumentUploadSuccess = () => {
    // Reload documents for this application (if we had an application ID)
    // For now, just show success
    showSuccess(t('documents.uploadSuccess', { defaultValue: 'Document uploaded successfully!' }));
  };

  const handleSubmit = async () => {
    if (!user?.id || !isValidUUID(user.id)) {
      setError('Invalid user ID. Please log in again.');
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      const submitData: ServiceApplicationRequest = {
        ...formData,
        schemeId: finalSchemeId || formData.schemeId,
        expectedCompletionDate: formData.expectedCompletionDate || undefined,
      };

      const application = await applicationService.createApplication(user.id, submitData);

      const successMessage = t('application.submit.success', { defaultValue: 'Application submitted successfully!' });
      showSuccess(successMessage);
      setTimeout(() => {
        navigate(`/applications/${application.id}`, {
          state: { message: successMessage },
        });
      }, 2000);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || t('application.submit.errors.submitFailed', { defaultValue: 'Failed to submit application' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('application.submit.title', { defaultValue: 'Application Details' })}
            </Typography>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              {scheme && (
                <Grid item xs={12}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                        <DescriptionIcon color="primary" />
                        <Box>
                          <Typography variant="subtitle1" fontWeight="bold">
                            {getSchemeName(scheme, i18n.language)}
                          </Typography>
                          {scheme.code && (
                            <Typography variant="body2" color="text.secondary">
                              {t('application.submit.schemeCode', { defaultValue: 'Scheme Code' })}: {scheme.code}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              <Grid item xs={12} md={6}>
                <FormControl fullWidth required>
                  <InputLabel>{t('application.submit.serviceType', { defaultValue: 'Service Type' })}</InputLabel>
                  <Select
                    value={formData.serviceType || ''}
                    label={t('application.submit.serviceType', { defaultValue: 'Service Type' })}
                    onChange={(e: SelectChangeEvent) => handleInputChange('serviceType', e.target.value)}
                  >
                    {serviceTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {t(`application.submit.serviceTypes.${type.key}`, { defaultValue: type.value })}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>{t('application.submit.applicationType', { defaultValue: 'Application Type' })}</InputLabel>
                  <Select
                    value={formData.applicationType || ''}
                    label={t('application.submit.applicationType', { defaultValue: 'Application Type' })}
                    onChange={(e: SelectChangeEvent) => handleInputChange('applicationType', e.target.value)}
                  >
                    {applicationTypes.map((type) => (
                      <MenuItem key={type.value} value={type.value}>
                        {t(`application.submit.applicationTypes.${type.key}`, { defaultValue: type.value })}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('application.submit.subject', { defaultValue: 'Subject' })}
                  value={formData.subject || ''}
                  onChange={(e) => handleInputChange('subject', e.target.value)}
                  helperText={t('application.submit.subjectHelper', { defaultValue: 'Brief subject/title for your application' })}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('application.submit.description', { defaultValue: 'Description' })}
                  multiline
                  rows={4}
                  value={formData.description || ''}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  helperText={t('application.submit.descriptionHelper', { defaultValue: 'Detailed description of your application' })}
                  inputProps={{ maxLength: 5000 }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>{t('application.submit.priority', { defaultValue: 'Priority' })}</InputLabel>
                  <Select
                    value={formData.priority || 'NORMAL'}
                    label={t('application.submit.priority', { defaultValue: 'Priority' })}
                    onChange={(e: SelectChangeEvent) => handleInputChange('priority', e.target.value)}
                  >
                    <MenuItem value="LOW">{t('common.priority.low', { defaultValue: 'Low' })}</MenuItem>
                    <MenuItem value="NORMAL">{t('common.priority.normal', { defaultValue: 'Normal' })}</MenuItem>
                    <MenuItem value="HIGH">{t('common.priority.high', { defaultValue: 'High' })}</MenuItem>
                    <MenuItem value="URGENT">{t('common.priority.urgent', { defaultValue: 'Urgent' })}</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label={t('application.submit.expectedCompletionDate', { defaultValue: 'Expected Completion Date' })}
                  type="date"
                  value={formData.expectedCompletionDate || ''}
                  onChange={(e) => handleInputChange('expectedCompletionDate', e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  helperText={t('application.submit.expectedCompletionDateHelper', { defaultValue: 'When do you expect this to be completed? (Optional)' })}
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('application.submit.uploadDocuments', { defaultValue: 'Upload Documents' })}
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              {t('application.submit.uploadDocumentsInfo', { 
                defaultValue: 'Upload any required documents for this application. You can also upload documents after submission.' 
              })}
            </Alert>
            {user?.id && isValidUUID(user.id) ? (
              <DocumentUpload
                citizenId={user.id}
                applicationId={undefined} // Will be set after application is created
                onUploadSuccess={handleDocumentUploadSuccess}
              />
            ) : (
              <Alert severity="warning">
                {t('application.submit.completeProfileWarning', { 
                  defaultValue: 'Please complete your profile before uploading documents.' 
                })}
              </Alert>
            )}
          </Box>
        );

      case 2:
        // Additional Information - only show if department has raised a query
        if (!hasDepartmentQuery) {
          // This step should be skipped, but if we're here, go to review
          return renderStepContent(3);
        }
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('application.submit.additionalInformation', { defaultValue: 'Additional Information' })}
            </Typography>
            <Alert severity="info" sx={{ mb: 3 }}>
              {t('application.submit.queryRaised', { 
                defaultValue: 'The department has raised a query regarding your application. Please provide the requested information below.' 
              })}
            </Alert>
            <Grid container spacing={3} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label={t('application.submit.queryResponse', { defaultValue: 'Response to Query' })}
                  multiline
                  rows={6}
                  value={formData.applicationData?.queryResponse || ''}
                  onChange={(e) => handleInputChange('applicationData', { ...formData.applicationData, queryResponse: e.target.value })}
                  helperText={t('application.submit.queryResponseHelper', { 
                    defaultValue: 'Please provide detailed information as requested by the department' 
                  })}
                />
              </Grid>
            </Grid>
          </Box>
        );

      case 3:
        return (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('application.submit.reviewTitle', { defaultValue: 'Review & Submit' })}
            </Typography>
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Grid container spacing={2}>
                  {scheme && (
                    <>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                          {t('application.scheme', { defaultValue: 'Scheme' })}
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          {getSchemeName(scheme, i18n.language)}
                        </Typography>
                      </Grid>
                      {scheme.code && (
                        <Grid item xs={12} sm={4}>
                          <Typography variant="body2" color="text.secondary">
                            {t('application.submit.schemeCode', { defaultValue: 'Scheme Code' })}
                          </Typography>
                          <Typography variant="body1">{scheme.code}</Typography>
                        </Grid>
                      )}
                    </>
                  )}
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      {t('application.submit.serviceType', { defaultValue: 'Service Type' })}
                    </Typography>
                    <Typography variant="body1" fontWeight="bold">
                      {(() => {
                        const serviceType = serviceTypes.find(st => st.value === formData.serviceType);
                        return serviceType 
                          ? t(`application.submit.serviceTypes.${serviceType.key}`, { defaultValue: serviceType.value })
                          : (formData.serviceType || 'N/A');
                      })()}
                    </Typography>
                  </Grid>
                  {formData.applicationType && (
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2" color="text.secondary">
                        {t('application.submit.applicationType', { defaultValue: 'Application Type' })}
                      </Typography>
                      <Typography variant="body1">
                        {(() => {
                          const appType = applicationTypes.find(at => at.value === formData.applicationType);
                          return appType 
                            ? t(`application.submit.applicationTypes.${appType.key}`, { defaultValue: appType.value })
                            : formData.applicationType;
                        })()}
                      </Typography>
                    </Grid>
                  )}
                  {formData.subject && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        {t('application.submit.subject', { defaultValue: 'Subject' })}
                      </Typography>
                      <Typography variant="body1">{formData.subject}</Typography>
                    </Grid>
                  )}
                  {formData.description && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary">
                        {t('application.submit.description', { defaultValue: 'Description' })}
                      </Typography>
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {formData.description}
                      </Typography>
                    </Grid>
                  )}
                  <Grid item xs={12} sm={4}>
                    <Typography variant="body2" color="text.secondary">
                      {t('application.submit.priority', { defaultValue: 'Priority' })}
                    </Typography>
                    <Typography variant="body1">{formData.priority || 'NORMAL'}</Typography>
                  </Grid>
                  {formData.expectedCompletionDate && (
                    <Grid item xs={12} sm={4}>
                      <Typography variant="body2" color="text.secondary">
                        {t('application.submit.expectedCompletionDate', { defaultValue: 'Expected Completion Date' })}
                      </Typography>
                      <Typography variant="body1">
                        {new Date(formData.expectedCompletionDate).toLocaleDateString()}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
            <Alert severity="warning" sx={{ mt: 3 }}>
              {t('application.submit.reviewWarning', { 
                defaultValue: 'Please review all information before submitting. Once submitted, you can track the application status in your Applications Hub.' 
              })}
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Please log in to submit an application</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Loading...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (!user?.id || !isValidUUID(user.id)) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          Please complete your profile before submitting an application.
        </Alert>
        <Button component="a" href="/profile" sx={{ mt: 2 }}>
          Complete Profile
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Back Button */}
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate(-1)} sx={{ mb: 3 }}>
        {t('application.submit.back', { defaultValue: 'Back' })}
      </Button>

      {/* Header */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <AssignmentIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          <Box>
            <Typography variant="h4" component="h1" fontWeight="bold">
              {t('application.submit.title', { defaultValue: 'Submit Application' })}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {scheme 
                ? `${t('application.submit.applyingFor', { defaultValue: 'Applying for' })}: ${getSchemeName(scheme, i18n.language)}`
                : t('application.submit.createNew', { defaultValue: 'Create a new service application' })
              }
            </Typography>
          </Box>
        </Box>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {[
            t('application.submit.steps.applicationDetails', { defaultValue: 'Application Details' }),
            t('application.submit.steps.documents', { defaultValue: 'Documents' }),
            t('application.submit.steps.additionalInformation', { defaultValue: 'Additional Information' }),
            t('application.submit.steps.reviewSubmit', { defaultValue: 'Review & Submit' }),
          ]
            .filter((_, index) => {
              // Hide Additional Information step if no department query
              if (index === 2 && !hasDepartmentQuery) return false;
              return true;
            })
            .map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
        </Stepper>
      </Paper>

      {/* Step Content */}
      <Paper sx={{ p: 4, mb: 3 }}>{renderStepContent(activeStep)}</Paper>

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={handleBack}
          startIcon={<ArrowBackIcon />}
        >
          {t('application.submit.back', { defaultValue: 'Back' })}
        </Button>
        <Box>
          {activeStep === 3 ? (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={submitting}
              startIcon={submitting ? <CircularProgress size={20} /> : <CheckCircleIcon />}
            >
              {submitting 
                ? t('application.submit.submitting', { defaultValue: 'Submitting...' })
                : t('application.submit.submitButton', { defaultValue: 'Submit Application' })
              }
            </Button>
          ) : (
            <Button variant="contained" onClick={handleNext}>
              {t('application.submit.next', { defaultValue: 'Next' })}
            </Button>
          )}
        </Box>
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

export default ApplicationSubmissionPage;

