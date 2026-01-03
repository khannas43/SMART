import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Grid,
  Divider,
  Card,
  CardContent,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  LocalOffer as SchemeIcon,
  CalendarToday as CalendarIcon,
  Business as DepartmentIcon,
  Category as CategoryIcon,
} from '@mui/icons-material';
import { schemeService } from '@/services';
import { Scheme } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

import { getSchemeName, getSchemeDescription } from '@/utils/localization';
import { formatEligibilityCriteria } from '@/utils/eligibilityCriteriaFormatter';
import { translateCategory, translateDepartment } from '@/utils/categoryTranslator';

const SchemeDetailsPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const { schemeId } = useParams<{ schemeId: string }>();
  const navigate = useNavigate();
  const { dialog, showError, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scheme, setScheme] = useState<Scheme | null>(null);

  useEffect(() => {
    if (schemeId) {
      loadSchemeDetails();
    }
  }, [schemeId]);

  const loadSchemeDetails = async () => {
    if (!schemeId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await schemeService.getSchemeById(schemeId);
      setScheme(data);
    } catch (err: any) {
      console.error('Error loading scheme details:', err);
      const errorMessage = err.message || t('schemes.errors.loadFailed', { defaultValue: 'Failed to load scheme details' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    const upperStatus = status.toUpperCase();
    if (upperStatus === 'ACTIVE') return 'success';
    if (upperStatus === 'INACTIVE' || upperStatus === 'CLOSED') return 'error';
    if (upperStatus === 'UPCOMING') return 'info';
    return 'default';
  };

  const handleApply = () => {
    // Navigate to application submission page
    if (schemeId) {
      navigate(`/applications/submit/${schemeId}`);
    } else {
      navigate('/applications/submit');
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {t('common.loading', { defaultValue: 'Loading...' })}
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error || !scheme) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/schemes')} sx={{ mb: 3 }}>
          {t('common.back', { defaultValue: 'Back to Schemes' })}
        </Button>
        <Alert severity="error">
          {error || t('schemes.details.notFound', { defaultValue: 'Scheme not found' })}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Paper sx={{ p: 4, mb: 3, position: 'relative' }}>
        {/* Back Button - Inside Paper, Top Right (positioned slightly down) */}
        <Box sx={{ position: 'absolute', top: 32, right: 24 }}>
          <Button 
            startIcon={<ArrowBackIcon />} 
            component={Link} 
            to="/schemes"
            variant="contained"
            color="primary"
          >
            {t('common.back', { defaultValue: 'Back' })}
          </Button>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 3 }}>
          <SchemeIcon sx={{ fontSize: 56, color: 'primary.main', mr: 3 }} />
          <Box sx={{ flexGrow: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
              <Typography variant="h4" component="h1">
                {getSchemeName(scheme, i18n.language)}
              </Typography>
              <Chip
                label={
                  scheme.status === 'ACTIVE' ? t('schemes.status.active', { defaultValue: 'Active' }) :
                  scheme.status === 'INACTIVE' ? t('schemes.status.inactive', { defaultValue: 'Inactive' }) :
                  scheme.status === 'UPCOMING' ? t('schemes.status.upcoming', { defaultValue: 'Upcoming' }) :
                  scheme.status || t('schemes.status.active', { defaultValue: 'Active' })
                }
                color={getStatusColor(scheme.status || 'ACTIVE')}
                size="medium"
              />
            </Box>

            {scheme.code && (
              <Typography variant="body1" color="text.secondary" gutterBottom>
                <strong>{t('schemes.details.code', { defaultValue: 'Scheme Code' })}:</strong> {scheme.code}
              </Typography>
            )}

            <Grid container spacing={2} sx={{ mt: 2 }}>
              {scheme.category && (
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CategoryIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {t('schemes.details.category', { defaultValue: 'Category' })}
                      </Typography>
                      <Typography variant="body2">{translateCategory(scheme.category, i18n.language)}</Typography>
                    </Box>
                  </Box>
                </Grid>
              )}

              {scheme.department && (
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <DepartmentIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {t('schemes.details.department', { defaultValue: 'Department' })}
                      </Typography>
                      <Typography variant="body2">{translateDepartment(scheme.department, i18n.language)}</Typography>
                    </Box>
                  </Box>
                </Grid>
              )}

              {scheme.startDate && scheme.endDate && (
                <Grid item xs={12} sm={6} md={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CalendarIcon color="action" />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {t('schemes.details.validity', { defaultValue: 'Valid From - To' })}
                      </Typography>
                      <Typography variant="body2">
                        {new Date(scheme.startDate).toLocaleDateString()} -{' '}
                        {new Date(scheme.endDate).toLocaleDateString()}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              )}
            </Grid>
          </Box>
        </Box>

        <Divider sx={{ my: 3 }} />

        {/* Action Buttons */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="contained" size="large" onClick={handleApply}>
            {t('schemes.details.checkEligibility', { defaultValue: 'Check Eligibility & Apply' })}
          </Button>
          <Button variant="outlined" size="large" onClick={() => navigate('/schemes/eligibility')}>
            {t('schemes.details.eligibilityChecker', { defaultValue: 'Eligibility Checker' })}
          </Button>
        </Box>
      </Paper>

      {/* Description */}
      {getSchemeDescription(scheme, i18n.language) && (
        <Paper sx={{ p: 4, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('schemes.details.description', { defaultValue: 'Description' })}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
            {getSchemeDescription(scheme, i18n.language)}
          </Typography>
        </Paper>
      )}

      {/* Eligibility Criteria */}
      {scheme.eligibilityCriteria && Object.keys(scheme.eligibilityCriteria).length > 0 && (
        <Paper sx={{ p: 4, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {t('schemes.details.eligibilityCriteria', { defaultValue: 'Eligibility Criteria' })}
          </Typography>
          <Card variant="outlined" sx={{ mt: 2 }}>
            <CardContent>
              <Grid container spacing={2}>
                {formatEligibilityCriteria(scheme.eligibilityCriteria, t).map((item, index) => (
                  <Grid item xs={12} sm={6} key={index}>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                      <Typography variant="body2" color="text.secondary" fontWeight="medium">
                        {item.label}:
                      </Typography>
                      <Typography variant="body1">{item.value}</Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Paper>
      )}

      {/* Additional Information */}
      <Paper sx={{ p: 4 }}>
        <Typography variant="h6" gutterBottom>
          {t('schemes.details.additionalInfo', { defaultValue: 'Additional Information' })}
        </Typography>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {scheme.createdAt && (
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>{t('schemes.details.createdAt', { defaultValue: 'Created At' })}:</strong>{' '}
                {new Date(scheme.createdAt).toLocaleDateString()}
              </Typography>
            </Grid>
          )}
          {scheme.updatedAt && (
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                <strong>{t('schemes.details.updatedAt', { defaultValue: 'Last Updated' })}:</strong>{' '}
                {new Date(scheme.updatedAt).toLocaleDateString()}
              </Typography>
            </Grid>
          )}
        </Grid>
      </Paper>

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

export default SchemeDetailsPage;

