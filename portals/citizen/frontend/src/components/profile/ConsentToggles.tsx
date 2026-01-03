import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  FormControlLabel,
  Switch,
  Paper,
  Grid,
  Chip,
  Divider,
} from '@mui/material';
import { useTranslation } from 'react-i18next';
import { ConsentPreference } from '@/types/api';
import { citizenService } from '@/services/citizen.service';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

interface ConsentTogglesProps {
  citizenId: string;
}

export const ConsentToggles: React.FC<ConsentTogglesProps> = ({ citizenId }) => {
  const { t } = useTranslation();
  const { dialog, showSuccess, showError, close } = useMessageDialog();
  const [preferences, setPreferences] = useState<ConsentPreference[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConsentPreferences();
  }, [citizenId]);

  const loadConsentPreferences = async () => {
    try {
      const data = await citizenService.getConsentPreferences(citizenId);
      // If no preferences exist, create default ones
      if (data.length === 0) {
        const defaultPreferences: ConsentPreference[] = [
          { field: 'fullName', fieldLabel: t('profile.fullName'), enabled: true, source: 'UIDAI' },
          { field: 'dateOfBirth', fieldLabel: t('profile.dateOfBirth'), enabled: true, source: 'UIDAI' },
          { field: 'gender', fieldLabel: t('profile.gender'), enabled: true, source: 'UIDAI' },
          { field: 'addressLine1', fieldLabel: t('labels.address'), enabled: false, source: 'Manual' },
          { field: 'email', fieldLabel: t('profile.email'), enabled: false, source: 'Manual' },
          { field: 'mobileNumber', fieldLabel: t('profile.mobileNumber'), enabled: true, source: 'UIDAI' },
          { field: 'incomeBand', fieldLabel: t('profile.incomeBand'), enabled: false, source: 'Inferred' },
          { field: 'vulnerabilityCategory', fieldLabel: t('profile.vulnerabilityCategory'), enabled: false, source: 'Inferred' },
        ];
        setPreferences(defaultPreferences);
      } else {
        // Translate field labels from backend
        const translatedData = data.map(pref => ({
          ...pref,
          fieldLabel: translateFieldLabel(pref.field, t),
        }));
        setPreferences(translatedData);
      }
    } catch (error: any) {
      console.warn('Consent preferences endpoint not available:', error?.response?.status || error?.message);
      // Use default preferences if endpoint is not available
      const defaultPreferences: ConsentPreference[] = [
        { field: 'fullName', fieldLabel: t('profile.fullName'), enabled: true, source: 'UIDAI' },
        { field: 'dateOfBirth', fieldLabel: t('profile.dateOfBirth'), enabled: true, source: 'UIDAI' },
        { field: 'gender', fieldLabel: t('profile.gender'), enabled: true, source: 'UIDAI' },
        { field: 'addressLine1', fieldLabel: t('labels.address'), enabled: false, source: 'Manual' },
        { field: 'email', fieldLabel: t('profile.email'), enabled: false, source: 'Manual' },
        { field: 'mobileNumber', fieldLabel: t('profile.mobileNumber'), enabled: true, source: 'UIDAI' },
        { field: 'incomeBand', fieldLabel: t('profile.incomeBand'), enabled: false, source: 'Inferred' },
        { field: 'vulnerabilityCategory', fieldLabel: t('profile.vulnerabilityCategory'), enabled: false, source: 'Inferred' },
      ];
      setPreferences(defaultPreferences);
      // Don't show error toast for optional endpoints
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (field: string, enabled: boolean) => {
    const updated = preferences.map((pref) =>
      pref.field === field ? { ...pref, enabled } : pref
    );
    setPreferences(updated);

    try {
      await citizenService.updateConsentPreferences(citizenId, updated);
      showSuccess(t('profile.consentPreferencesUpdated'));
    } catch (error) {
      console.error('Failed to update consent preferences:', error);
      showError(t('profile.failedToUpdateConsentPreferences'));
      // Revert on error
      loadConsentPreferences();
    }
  };

  // Helper function to translate field labels
  const translateFieldLabel = (field: string, t: any): string => {
    const fieldMap: Record<string, string> = {
      'fullName': t('profile.fullName'),
      'dateOfBirth': t('profile.dateOfBirth'),
      'gender': t('profile.gender'),
      'addressLine1': t('labels.address'),
      'email': t('profile.email'),
      'mobileNumber': t('profile.mobileNumber'),
      'incomeBand': t('profile.incomeBand'),
      'vulnerabilityCategory': t('profile.vulnerabilityCategory'),
    };
    return fieldMap[field] || field;
  };

  const getSourceColor = (source?: string): 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' => {
    switch (source) {
      case 'UIDAI':
        return 'success';
      case 'Manual':
        return 'warning';
      case 'Inferred':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading) {
    return <Typography>{t('profile.loadingConsentPreferences')}</Typography>;
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {t('profile.dataSharingConsent')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t('profile.dataSharingConsentDescription')}
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Grid container spacing={2}>
        {preferences.map((pref) => (
          <Grid item xs={12} sm={6} md={4} key={pref.field}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                p: 2,
                border: '1px solid #e0e0e0',
                borderRadius: 1,
              }}
            >
              <Box>
                <Typography variant="body1" fontWeight="medium">
                  {pref.fieldLabel}
                </Typography>
                {pref.source && (
                  <Chip
                    label={pref.source}
                    size="small"
                    color={getSourceColor(pref.source)}
                    sx={{ mt: 0.5 }}
                  />
                )}
              </Box>
              <FormControlLabel
                control={
                  <Switch
                    checked={pref.enabled}
                    onChange={(e) => handleToggle(pref.field, e.target.checked)}
                    color="primary"
                  />
                }
                label=""
              />
            </Box>
          </Grid>
        ))}
      </Grid>

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
    </Paper>
  );
};

