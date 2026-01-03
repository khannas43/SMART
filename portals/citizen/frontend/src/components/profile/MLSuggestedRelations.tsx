import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  Button,
  Chip,
  Grid,
  Avatar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  PersonAdd as PersonAddIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { MLSuggestedRelation } from '@/types/api';
import { citizenService } from '@/services/citizen.service';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { useTranslation } from 'react-i18next';
import { getUserName } from '@/utils/localization';

interface MLSuggestedRelationsProps {
  citizenId: string;
  onRelationAccepted?: () => void;
}

export const MLSuggestedRelations: React.FC<MLSuggestedRelationsProps> = ({
  citizenId,
  onRelationAccepted,
}) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const { dialog, showSuccess, showError, close } = useMessageDialog();
  const [suggestions, setSuggestions] = useState<MLSuggestedRelation[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);

  useEffect(() => {
    loadSuggestions();
  }, [citizenId]);

  const loadSuggestions = async () => {
    try {
      const data = await citizenService.getMLSuggestedRelations(citizenId);
      setSuggestions(data);
    } catch (error: any) {
      console.warn('ML suggested relations endpoint not available:', error?.response?.status || error?.message);
      // Don't show error toast for optional endpoints
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (suggestionId: string) => {
    setProcessing(suggestionId);
    try {
      await citizenService.acceptSuggestedRelation(citizenId, suggestionId);
      showSuccess(t('profile.familyRelationAccepted'));
      setSuggestions(suggestions.filter((s) => s.id !== suggestionId));
      if (onRelationAccepted) {
        onRelationAccepted();
      }
    } catch (error) {
      console.error('Failed to accept suggestion:', error);
      showError(t('profile.failedToAcceptFamilyRelation'));
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (suggestionId: string) => {
    setProcessing(suggestionId);
    try {
      await citizenService.rejectSuggestedRelation(citizenId, suggestionId);
      showSuccess(t('profile.suggestionDismissed'));
      setSuggestions(suggestions.filter((s) => s.id !== suggestionId));
    } catch (error) {
      console.error('Failed to reject suggestion:', error);
      showError(t('profile.failedToDismissSuggestion'));
    } finally {
      setProcessing(null);
    }
  };

  const getConfidenceColor = (confidence: number): 'success' | 'warning' | 'error' => {
    if (confidence >= 80) return 'success';
    if (confidence >= 60) return 'warning';
    return 'error';
  };

  if (loading) {
    return <Typography>{t('profile.loadingMLSuggestions')}</Typography>;
  }

  if (suggestions.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <PersonAddIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="body2" color="text.secondary">
          {t('profile.noSuggestedFamilyRelations')}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <PersonAddIcon color="primary" />
        <Typography variant="h6">
          {t('profile.mlSuggestedFamilyRelations')}
        </Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t('profile.aiIdentifiedPotentialMembers')}
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Grid container spacing={2}>
        {suggestions.map((suggestion) => (
          <Grid item xs={12} md={6} key={suggestion.id}>
            <Card variant="outlined">
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'start', gap: 2, mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', width: 56, height: 56 }}>
                    {getUserName({ fullName: suggestion.suggestedMember.name, fullNameHindi: suggestion.suggestedMember.nameHindi }, currentLanguage).charAt(0)}
                  </Avatar>
                  <Box sx={{ flexGrow: 1 }}>
                    <Typography variant="h6" gutterBottom>
                      {getUserName({ fullName: suggestion.suggestedMember.name, fullNameHindi: suggestion.suggestedMember.nameHindi }, currentLanguage)}
                    </Typography>
                    <Chip
                      label={suggestion.suggestedRelationship}
                      size="small"
                      color="primary"
                      sx={{ mb: 1 }}
                    />
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      <Chip
                        icon={<TrendingUpIcon />}
                        label={`${suggestion.confidence}% ${t('profile.confidence')}`}
                        size="small"
                        color={getConfidenceColor(suggestion.confidence)}
                      />
                      <Chip
                        label={`${suggestion.matchScore}% ${t('profile.match')}`}
                        size="small"
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </Box>

                {suggestion.suggestedMember.age && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {t('profile.age')}: {suggestion.suggestedMember.age}
                  </Typography>
                )}
                {suggestion.suggestedMember.gender && (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {t('profile.gender')}: {suggestion.suggestedMember.gender}
                  </Typography>
                )}

                {suggestion.reasons.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      {t('profile.whySuggested')}
                    </Typography>
                    <List dense>
                      {suggestion.reasons.map((reason, index) => (
                        <ListItem key={index} sx={{ py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircleIcon fontSize="small" color="success" />
                          </ListItemIcon>
                          <ListItemText primary={reason} />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<CheckCircleIcon />}
                    onClick={() => handleAccept(suggestion.id)}
                    disabled={processing === suggestion.id}
                    fullWidth
                  >
                    {t('profile.accept')}
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    startIcon={<CancelIcon />}
                    onClick={() => handleReject(suggestion.id)}
                    disabled={processing === suggestion.id}
                    fullWidth
                  >
                    {t('profile.dismiss')}
                  </Button>
                </Box>
              </CardContent>
            </Card>
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

