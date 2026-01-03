import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  CardActions,
  Chip,
  RadioGroup,
  FormControlLabel,
  Radio,
  Stepper,
  Step,
  StepLabel,
  Divider,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Warning as WarningIcon,
  LocalOffer as SchemeIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { schemeService, citizenService } from '@/services';
import { Scheme } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { useAppSelector } from '@/store/hooks';

interface QuestionnaireData {
  age?: number;
  gender?: string;
  district?: string;
  annualIncome?: number;
  incomeGroup?: string;
  familySize?: number;
  disability?: boolean;
  occupation?: string;
  hasRationCard?: boolean;
}

interface EligibilityResult {
  scheme: Scheme;
  eligible: boolean;
  confidence: number;
  reasons: string[];
  missingCriteria?: string[];
}

import { getSchemeName, getSchemeDescription } from '@/utils/localization';

const EligibilityCheckerPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const schemeIdParam = searchParams.get('schemeId');
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadingSchemes, setLoadingSchemes] = useState(true);
  const [loadingUserData, setLoadingUserData] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [questionnaireData, setQuestionnaireData] = useState<QuestionnaireData>({});
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [selectedScheme, setSelectedScheme] = useState<Scheme | null>(null);
  const [eligibilityResults, setEligibilityResults] = useState<EligibilityResult[]>([]);

  const steps = [
    t('eligibility.steps.questionnaire', { defaultValue: 'Questionnaire' }),
    t('eligibility.steps.results', { defaultValue: 'Results' }),
  ];

  useEffect(() => {
    loadSchemes();
    if (isAuthenticated && user?.id) {
      loadUserData();
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    if (schemeIdParam && schemes.length > 0) {
      const scheme = schemes.find((s) => s.id === schemeIdParam);
      if (scheme) {
        setSelectedScheme(scheme);
      }
    }
  }, [schemeIdParam, schemes]);

  const loadUserData = async () => {
    if (!user?.id) return;
    
    setLoadingUserData(true);
    try {
      const userData = await citizenService.getCitizenById(user.id);
      
      // Calculate age from date of birth
      let age: number | undefined;
      if (userData.dateOfBirth) {
        const birthDate = new Date(userData.dateOfBirth);
        const today = new Date();
        age = today.getFullYear() - birthDate.getFullYear();
        const monthDiff = today.getMonth() - birthDate.getMonth();
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
          age--;
        }
      }

      // Auto-fill questionnaire data
      setQuestionnaireData((prev) => ({
        ...prev,
        age: age,
        gender: userData.gender,
        district: userData.district,
        // Note: We don't have annualIncome or familySize in user data, so those remain empty
        // User can fill them manually
      }));
    } catch (err: any) {
      console.warn('Failed to load user data for auto-fill:', err);
      // Don't show error - just continue without auto-fill
    } finally {
      setLoadingUserData(false);
    }
  };

  const loadSchemes = async () => {
    setLoadingSchemes(true);
    try {
      const data = await schemeService.getSchemes(0, 100, 'ACTIVE');
      setSchemes(data.content);
    } catch (err: any) {
      console.error('Error loading schemes:', err);
      showError(t('schemes.errors.loadFailed', { defaultValue: 'Failed to load schemes' }));
    } finally {
      setLoadingSchemes(false);
    }
  };

  const handleInputChange = (field: keyof QuestionnaireData, value: any) => {
    setQuestionnaireData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const validateQuestionnaire = (): boolean => {
    if (!questionnaireData.age || questionnaireData.age < 1 || questionnaireData.age > 120) {
      showError(t('eligibility.errors.invalidAge', { defaultValue: 'Please enter a valid age' }));
      return false;
    }
    if (!questionnaireData.gender) {
      showError(t('eligibility.errors.selectGender', { defaultValue: 'Please select gender' }));
      return false;
    }
    if (!questionnaireData.district) {
      showError(t('eligibility.errors.selectDistrict', { defaultValue: 'Please select district' }));
      return false;
    }
    return true;
  };

  const checkEligibility = async () => {
    if (!validateQuestionnaire()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Simulate eligibility checking logic
      // TODO: Replace with actual eligibility API call when available
      await new Promise((resolve) => setTimeout(resolve, 1500));

      // Basic eligibility logic (placeholder - will be replaced with AI/ML API)
      const results: EligibilityResult[] = schemes.map((scheme) => {
        const reasons: string[] = [];
        const missingCriteria: string[] = [];
        let eligible = true;

        // Basic age check (example)
        if (scheme.eligibilityCriteria?.minAge && questionnaireData.age) {
          if (questionnaireData.age < (scheme.eligibilityCriteria.minAge as number)) {
            eligible = false;
            missingCriteria.push(
              `Age requirement: ${scheme.eligibilityCriteria.minAge}+ years`
            );
          } else {
            reasons.push(`Age requirement met (${questionnaireData.age} years)`);
          }
        }

        // Basic income check (example)
        if (scheme.eligibilityCriteria?.maxIncome && questionnaireData.annualIncome) {
          if (questionnaireData.annualIncome > (scheme.eligibilityCriteria.maxIncome as number)) {
            eligible = false;
            missingCriteria.push(
              `Income limit: Up to ₹${scheme.eligibilityCriteria.maxIncome}`
            );
          } else {
            reasons.push(`Income within limit`);
          }
        }

        // Basic district check (example)
        if (scheme.eligibilityCriteria?.districts && questionnaireData.district) {
          const allowedDistricts = scheme.eligibilityCriteria.districts as string[];
          if (!allowedDistricts.includes(questionnaireData.district)) {
            eligible = false;
            missingCriteria.push(`Available only in: ${allowedDistricts.join(', ')}`);
          } else {
            reasons.push(`District requirement met`);
          }
        }

        // Calculate confidence based on how many criteria we can check
        const confidence = reasons.length > 0 ? Math.min(90, reasons.length * 30) : 50;

        return {
          scheme,
          eligible,
          confidence,
          reasons,
          missingCriteria: missingCriteria.length > 0 ? missingCriteria : undefined,
        };
      });

      // Filter to selected scheme if provided
      const filteredResults = selectedScheme
        ? results.filter((r) => r.scheme.id === selectedScheme.id)
        : results;

      // Sort: eligible first, then by confidence
      filteredResults.sort((a, b) => {
        if (a.eligible && !b.eligible) return -1;
        if (!a.eligible && b.eligible) return 1;
        return b.confidence - a.confidence;
      });

      setEligibilityResults(filteredResults);
      setActiveStep(1);
      showSuccess(t('eligibility.checkComplete', { defaultValue: 'Eligibility check completed' }));
    } catch (err: any) {
      console.error('Error checking eligibility:', err);
      const errorMessage = err.message || t('eligibility.errors.checkFailed', { defaultValue: 'Failed to check eligibility' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };


  const getEligibilityColor = (eligible: boolean): 'success' | 'error' | 'warning' => {
    return eligible ? 'success' : 'error';
  };

  // Districts list (could be fetched from API in future)
  const districts = [
    'Ajmer',
    'Alwar',
    'Banswara',
    'Baran',
    'Barmer',
    'Bharatpur',
    'Bhilwara',
    'Bikaner',
    'Bundi',
    'Chittorgarh',
    'Churu',
    'Dausa',
    'Dholpur',
    'Dungarpur',
    'Ganganagar',
    'Hanumangarh',
    'Jaipur',
    'Jaisalmer',
    'Jalore',
    'Jhalawar',
    'Jhunjhunu',
    'Jodhpur',
    'Karauli',
    'Kota',
    'Nagaur',
    'Pali',
    'Pratapgarh',
    'Rajsamand',
    'Sawai Madhopur',
    'Sikar',
    'Sirohi',
    'Sri Ganganagar',
    'Tonk',
    'Udaipur',
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('eligibility.title', { defaultValue: 'Eligibility Checker' })}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('eligibility.subtitle', {
            defaultValue: 'Answer a few questions to check your eligibility for government schemes',
          })}
        </Typography>
      </Box>

      {/* Stepper */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Stepper activeStep={activeStep}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Step 0: Questionnaire */}
      {activeStep === 0 && (
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
            {t('eligibility.questionnaire.title', { defaultValue: 'Personal Information' })}
          </Typography>

          <Grid container spacing={3}>
            {/* Age */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('eligibility.questionnaire.age', { defaultValue: 'Age' })}
                type="number"
                value={questionnaireData.age || ''}
                onChange={(e) => handleInputChange('age', parseInt(e.target.value) || undefined)}
                inputProps={{ min: 1, max: 120 }}
                required
              />
            </Grid>

            {/* Gender */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>{t('eligibility.questionnaire.gender', { defaultValue: 'Gender' })}</InputLabel>
                <Select
                  value={questionnaireData.gender || ''}
                  label={t('eligibility.questionnaire.gender', { defaultValue: 'Gender' })}
                  onChange={(e) => handleInputChange('gender', e.target.value)}
                >
                  <MenuItem value="MALE">{t('common.gender.male')}</MenuItem>
                  <MenuItem value="FEMALE">{t('common.gender.female')}</MenuItem>
                  <MenuItem value="OTHER">{t('common.gender.other')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* District */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>{t('eligibility.questionnaire.district', { defaultValue: 'District' })}</InputLabel>
                <Select
                  value={questionnaireData.district || ''}
                  label={t('eligibility.questionnaire.district', { defaultValue: 'District' })}
                  onChange={(e) => handleInputChange('district', e.target.value)}
                >
                  {districts.map((district) => (
                    <MenuItem key={district} value={district}>
                      {district}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Annual Income */}
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label={t('eligibility.questionnaire.annualIncome', { defaultValue: 'Annual Income (₹)' })}
                type="number"
                value={questionnaireData.annualIncome || ''}
                onChange={(e) => handleInputChange('annualIncome', parseFloat(e.target.value) || undefined)}
                inputProps={{ min: 0, step: 1000 }}
              />
            </Grid>

            {/* Income Group */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('eligibility.questionnaire.incomeGroup', { defaultValue: 'Income Group' })}</InputLabel>
                <Select
                  value={questionnaireData.incomeGroup || ''}
                  label={t('eligibility.questionnaire.incomeGroup', { defaultValue: 'Income Group' })}
                  onChange={(e) => handleInputChange('incomeGroup', e.target.value)}
                >
                  <MenuItem value="BPL">
                    {t('eligibility.incomeGroup.bpl', { defaultValue: 'BPL (Below Poverty Line)' })}
                  </MenuItem>
                  <MenuItem value="APL">
                    {t('eligibility.incomeGroup.apl', { defaultValue: 'APL (Above Poverty Line)' })}
                  </MenuItem>
                  <MenuItem value="HIGH">
                    {t('eligibility.incomeGroup.high', { defaultValue: 'High Income' })}
                  </MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Family Size */}
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>{t('eligibility.questionnaire.familySize', { defaultValue: 'Family Size' })}</InputLabel>
                <Select
                  value={questionnaireData.familySize || ''}
                  label={t('eligibility.questionnaire.familySize', { defaultValue: 'Family Size' })}
                  onChange={(e) => handleInputChange('familySize', parseInt(e.target.value) || undefined)}
                >
                  {Array.from({ length: 20 }, (_, i) => i + 1).map((size) => (
                    <MenuItem key={size} value={size}>
                      {size}
                    </MenuItem>
                  ))}
                  <MenuItem value={25}>25+</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {/* Disability Status */}
            <Grid item xs={12} sm={6}>
              <FormControl component="fieldset">
                <Typography variant="body2" gutterBottom>
                  {t('eligibility.questionnaire.disability', { defaultValue: 'Disability Status' })}
                </Typography>
                <RadioGroup
                  row
                  value={questionnaireData.disability ? 'yes' : 'no'}
                  onChange={(e) => handleInputChange('disability', e.target.value === 'yes')}
                >
                  <FormControlLabel value="yes" control={<Radio />} label={t('common.yes', { defaultValue: 'Yes' })} />
                  <FormControlLabel value="no" control={<Radio />} label={t('common.no', { defaultValue: 'No' })} />
                </RadioGroup>
              </FormControl>
            </Grid>

            {/* Has Ration Card */}
            <Grid item xs={12} sm={6}>
              <FormControl component="fieldset">
                <Typography variant="body2" gutterBottom>
                  {t('eligibility.questionnaire.hasRationCard', { defaultValue: 'Do you have a Ration Card?' })}
                </Typography>
                <RadioGroup
                  row
                  value={questionnaireData.hasRationCard ? 'yes' : 'no'}
                  onChange={(e) => handleInputChange('hasRationCard', e.target.value === 'yes')}
                >
                  <FormControlLabel value="yes" control={<Radio />} label={t('common.yes', { defaultValue: 'Yes' })} />
                  <FormControlLabel value="no" control={<Radio />} label={t('common.no', { defaultValue: 'No' })} />
                </RadioGroup>
              </FormControl>
            </Grid>
          </Grid>

          {/* Selected Scheme Info */}
          {selectedScheme && (
            <Box sx={{ mt: 4, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
              <Typography variant="body2" gutterBottom>
                <strong>
                  {t('eligibility.checkingForScheme', {
                    defaultValue: 'Checking eligibility for:',
                  })}{' '}
                </strong>
                {getSchemeName(selectedScheme, i18n.language)}
              </Typography>
            </Box>
          )}

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4 }}>
            <Button variant="outlined" onClick={() => navigate('/schemes')}>
              {t('common.cancel', { defaultValue: 'Cancel' })}
            </Button>
            <Button variant="contained" onClick={checkEligibility} disabled={loading}>
              {loading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  {t('eligibility.checking', { defaultValue: 'Checking...' })}
                </>
              ) : (
                t('eligibility.checkEligibility', { defaultValue: 'Check Eligibility' })
              )}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Step 1: Results */}
      {activeStep === 1 && (
        <>
          {/* Summary */}
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              {t('eligibility.results.summary', { defaultValue: 'Eligibility Results Summary' })}
            </Typography>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12} sm={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <CheckCircleIcon sx={{ fontSize: 40, color: 'success.main' }} />
                  <Typography variant="h5" color="success.main">
                    {eligibilityResults.filter((r) => r.eligible).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('eligibility.results.eligible', { defaultValue: 'Eligible Schemes' })}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <CancelIcon sx={{ fontSize: 40, color: 'error.main' }} />
                  <Typography variant="h5" color="error.main">
                    {eligibilityResults.filter((r) => !r.eligible).length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('eligibility.results.notEligible', { defaultValue: 'Not Eligible' })}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ textAlign: 'center' }}>
                  <SchemeIcon sx={{ fontSize: 40, color: 'primary.main' }} />
                  <Typography variant="h5" color="primary.main">
                    {eligibilityResults.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('eligibility.results.totalChecked', { defaultValue: 'Total Checked' })}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Results Grid */}
          <Grid container spacing={3}>
            {eligibilityResults.map((result) => (
              <Grid item xs={12} sm={6} md={4} key={result.scheme.id}>
                <Card
                  variant="outlined"
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    borderLeft: `4px solid ${
                      result.eligible ? 'success.main' : 'error.main'
                    }`,
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4,
                    },
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                        <Typography variant="h6" sx={{ fontSize: '1.1rem', flexGrow: 1 }}>
                          {getSchemeName(result.scheme, i18n.language)}
                        </Typography>
                        <Chip
                          label={result.eligible ? t('eligibility.eligible', { defaultValue: 'Eligible' }) : t('eligibility.notEligible', { defaultValue: 'Not Eligible' })}
                          color={getEligibilityColor(result.eligible)}
                          size="small"
                        />
                        <Chip
                          label={`${result.confidence}%`}
                          size="small"
                          variant="outlined"
                          color={result.confidence >= 80 ? 'success' : result.confidence >= 50 ? 'warning' : 'error'}
                        />
                      </Box>
                    </Box>

                    {result.scheme.code && (
                      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1.5 }}>
                        {t('schemes.browse.code', { defaultValue: 'Code' })}: {result.scheme.code}
                      </Typography>
                    )}

                    {/* Confidence Reason - Show for 50% confidence */}
                    {result.confidence === 50 && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="body2" fontWeight="medium" gutterBottom sx={{ fontSize: '0.85rem' }}>
                          {t('eligibility.results.confidenceReason', { defaultValue: 'Confidence Level Reason:' })}
                        </Typography>
                        <Typography variant="body2" sx={{ fontSize: '0.8rem', color: 'text.secondary' }}>
                          {t('eligibility.results.confidenceReasonText')}
                        </Typography>
                      </Box>
                    )}

                    {/* Reasons - Show for eligible or 50%+ confidence */}
                    {(result.reasons.length > 0 && (result.eligible || result.confidence >= 50)) && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="body2" fontWeight="medium" gutterBottom sx={{ fontSize: '0.85rem' }}>
                          {result.eligible 
                            ? t('eligibility.results.whyEligible', { defaultValue: 'Why Eligible:' })
                            : t('eligibility.results.reasons', { defaultValue: 'Reasons:' })}
                        </Typography>
                        <Box component="ul" sx={{ margin: 0, paddingLeft: 2, fontSize: '0.8rem' }}>
                          {result.reasons.slice(0, 3).map((reason, idx) => (
                            <li key={idx}>
                              <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{reason}</Typography>
                            </li>
                          ))}
                          {result.reasons.length > 3 && (
                            <Typography variant="caption" color="text.secondary">
                              +{result.reasons.length - 3} {t('common.more', { defaultValue: 'more' })}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    )}

                    {/* Missing Criteria */}
                    {result.missingCriteria && result.missingCriteria.length > 0 && (
                      <Box sx={{ mb: 1.5 }}>
                        <Typography variant="body2" color="error.main" fontWeight="medium" gutterBottom sx={{ fontSize: '0.85rem' }}>
                          {t('eligibility.results.missingCriteria', {
                            defaultValue: 'Missing Criteria:',
                          })}
                        </Typography>
                        <Box component="ul" sx={{ margin: 0, paddingLeft: 2, fontSize: '0.8rem' }}>
                          {result.missingCriteria.slice(0, 2).map((criteria, idx) => (
                            <li key={idx}>
                              <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>{criteria}</Typography>
                            </li>
                          ))}
                          {result.missingCriteria.length > 2 && (
                            <Typography variant="caption" color="text.secondary">
                              +{result.missingCriteria.length - 2} {t('common.more')}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    )}

                    {result.scheme.description && (
                      <Typography 
                        variant="body2" 
                        color="text.secondary" 
                        sx={{ 
                          mt: 1,
                          fontSize: '0.8rem',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {getSchemeDescription(result.scheme, i18n.language)}
                      </Typography>
                    )}
                  </CardContent>
                  <CardActions sx={{ p: 1.5, pt: 0 }}>
                    <Button
                      size="small"
                      component={Link}
                      to={`/schemes/${result.scheme.id}`}
                      endIcon={<ArrowForwardIcon />}
                      sx={{ fontSize: '0.75rem' }}
                    >
                      {t('common.viewDetails', { defaultValue: 'View Details' })}
                    </Button>
                    {result.eligible && (
                      <Button
                        size="small"
                        variant="contained"
                        onClick={() => {
                          navigate(`/applications/new?schemeId=${result.scheme.id}`);
                        }}
                        sx={{ fontSize: '0.75rem' }}
                      >
                        {t('eligibility.applyNow', { defaultValue: 'Apply Now' })}
                      </Button>
                    )}
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Action Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 4 }}>
            {activeStep > 0 && (
              <Button variant="outlined" onClick={() => setActiveStep(0)}>
                {t('common.back', { defaultValue: 'Back' })} {t('eligibility.steps.questionnaire', { defaultValue: 'to Questionnaire' })}
              </Button>
            )}
            <Button variant="outlined" onClick={() => navigate('/schemes')}>
              {t('common.browseSchemes')}
            </Button>
          </Box>
        </>
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

export default EligibilityCheckerPage;

