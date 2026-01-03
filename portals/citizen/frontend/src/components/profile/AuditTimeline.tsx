import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  Divider,
  Avatar,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { AuditEntry } from '@/types/api';
import { citizenService } from '@/services/citizen.service';
import { useTranslation } from 'react-i18next';
// Format date helper
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateString;
  }
};
import toast from 'react-hot-toast';

interface AuditTimelineProps {
  citizenId: string;
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ citizenId }) => {
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuditTimeline();
  }, [citizenId]);

  const loadAuditTimeline = async () => {
    try {
      const data = await citizenService.getAuditTimeline(citizenId);
      // Sort by date (newest first)
      const sorted = data.sort((a, b) => 
        new Date(b.changedAt).getTime() - new Date(a.changedAt).getTime()
      );
      setEntries(sorted);
    } catch (error: any) {
      console.warn('Audit timeline endpoint not available:', error?.response?.status || error?.message);
      // Don't show error toast for optional endpoints
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceDelta = (entry: AuditEntry): number | null => {
    if (entry.oldConfidence !== undefined && entry.newConfidence !== undefined) {
      return entry.newConfidence - entry.oldConfidence;
    }
    return null;
  };

  const getConfidenceColor = (confidence?: number): 'success' | 'warning' | 'error' => {
    if (!confidence) return 'success';
    if (confidence >= 95) return 'success';
    if (confidence >= 80) return 'warning';
    return 'error';
  };

  const getChangedByIcon = (type: string) => {
    switch (type) {
      case 'USER':
        return <PersonIcon />;
      case 'SYSTEM':
        return <InfoIcon />;
      case 'AUTOMATED':
        return <CheckCircleIcon />;
      default:
        return <InfoIcon />;
    }
  };

  if (loading) {
    return <Typography>{t('profile.loadingAuditTimeline')}</Typography>;
  }

  if (entries.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          {t('profile.noAuditHistoryAvailable')}
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {t('profile.goldenRecordAuditTimeline')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        {t('profile.changeHistoryConfidence')}
      </Typography>
      <Divider sx={{ mb: 2 }} />
      <Box>
        {entries.map((entry, index) => {
          const delta = getConfidenceDelta(entry);
          const isLast = index === entries.length - 1;

          return (
            <Box key={entry.id} sx={{ display: 'flex', mb: 3, position: 'relative' }}>
              {/* Timeline line and dot */}
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mr: 2 }}>
                <Avatar
                  sx={{
                    bgcolor: getConfidenceColor(entry.newConfidence) === 'success' ? 'success.main' :
                             getConfidenceColor(entry.newConfidence) === 'warning' ? 'warning.main' : 'error.main',
                    width: 40,
                    height: 40,
                  }}
                >
                  {getChangedByIcon(entry.changedByType)}
                </Avatar>
                {!isLast && (
                  <Box
                    sx={{
                      width: 2,
                      flexGrow: 1,
                      bgcolor: 'divider',
                      minHeight: 40,
                      mt: 1,
                    }}
                  />
                )}
              </Box>

              {/* Content */}
              <Box sx={{ flexGrow: 1 }}>
                <Paper sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {entry.fieldLabel}
                    </Typography>
                    <Chip
                      label={entry.changedByType}
                      size="small"
                      color={entry.changedByType === 'USER' ? 'primary' : 'default'}
                    />
                  </Box>
                  
                  {entry.oldValue && entry.newValue && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        <strong>{t('profile.from')}:</strong> {entry.oldValue}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        <strong>{t('profile.to')}:</strong> {entry.newValue}
                      </Typography>
                    </Box>
                  )}

                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                    {entry.oldConfidence !== undefined && (
                      <Chip
                        label={`${t('profile.old')}: ${entry.oldConfidence}%`}
                        size="small"
                        color={getConfidenceColor(entry.oldConfidence)}
                      />
                    )}
                    {entry.newConfidence !== undefined && (
                      <Chip
                        label={`${t('profile.new')}: ${entry.newConfidence}%`}
                        size="small"
                        color={getConfidenceColor(entry.newConfidence)}
                      />
                    )}
                    {delta !== null && (
                      <Chip
                        label={delta > 0 ? `+${delta}%` : `${delta}%`}
                        size="small"
                        color={delta > 0 ? 'success' : 'error'}
                      />
                    )}
                    <Chip label={`${t('profile.source')}: ${entry.source}`} size="small" variant="outlined" />
                  </Box>

                  <Typography variant="caption" color="text.secondary">
                    {formatDate(entry.changedAt)} by {entry.changedBy}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          );
        })}
      </Box>
    </Paper>
  );
};

