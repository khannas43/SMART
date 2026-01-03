import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  Chip,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Person as PersonIcon,
  ArrowBack as ArrowBackIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  LocationOn as LocationIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { citizenService } from '@/services';
import { FamilyMember } from '@/types/api';
import { getUserName } from '@/utils/localization';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';

// Helper function to translate relationship types
const translateRelationship = (relationship: string, t: any): string => {
  const relationshipMap: Record<string, string> = {
    'Spouse': t('profile.spouse'),
    'Child': t('profile.child'),
    'Parent': t('profile.parent'),
    'Sibling': t('profile.sibling'),
    'Family Member': t('profile.familyMember'),
    'Self': t('profile.self'),
  };
  return relationshipMap[relationship] || relationship;
};

export const FamilyMemberProfilePage: React.FC = () => {
  const { memberId } = useParams<{ memberId: string }>();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.language;
  const { dialog, showError, close } = useMessageDialog();

  const [loading, setLoading] = useState(true);
  const [member, setMember] = useState<FamilyMember | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!memberId) {
      setError('Family member ID is required');
      setLoading(false);
      return;
    }

    loadFamilyMember();
  }, [memberId]);

  const loadFamilyMember = async () => {
    if (!memberId || !user?.id) return;

    try {
      setLoading(true);
      setError(null);

      // First, try to load from family relationships
      const familyGraph = await citizenService.getFamilyRelationships(user.id, 3);
      const foundMember = familyGraph.members.find((m) => m.id === memberId);

      if (foundMember) {
        // If we have a member from family graph, try to fetch full citizen data to get complete Aadhaar number
        try {
          const citizen = await citizenService.getCitizenById(memberId);
          // Merge family member data with full citizen data (prefer citizen data for Aadhaar)
          const enrichedMember: FamilyMember = {
            ...foundMember,
            aadhaarNumber: citizen.janAadhaarId || foundMember.aadhaarNumber,
            mobileNumber: citizen.mobileNumber || foundMember.mobileNumber,
            dateOfBirth: citizen.dateOfBirth || foundMember.dateOfBirth,
          };
          setMember(enrichedMember);
        } catch (citizenErr) {
          // If citizen fetch fails, use the family member data as-is
          console.warn('Could not fetch full citizen data, using family member data:', citizenErr);
          setMember(foundMember);
        }
      } else {
        // If not found in family graph, try to load as a citizen directly
        // This handles cases where the member ID is a real citizen UUID
        try {
          const citizen = await citizenService.getCitizenById(memberId);
          // Convert Citizen (User) to FamilyMember format
          const familyMember: FamilyMember = {
            id: citizen.id,
            name: citizen.fullName || 'Unknown',
            relationship: 'Family Member',
            age: citizen.dateOfBirth ? new Date().getFullYear() - new Date(citizen.dateOfBirth).getFullYear() : undefined,
            gender: citizen.gender as 'MALE' | 'FEMALE' | 'OTHER' | undefined,
            confidence: 100,
            aadhaarNumber: citizen.janAadhaarId || undefined,
            mobileNumber: citizen.mobileNumber,
            dateOfBirth: citizen.dateOfBirth,
          };
          setMember(familyMember);
        } catch (citizenErr: any) {
          console.error('Failed to load as citizen:', citizenErr);
          // If it's a 404, the member doesn't exist in the database
          if (citizenErr?.response?.status === 404) {
            setError('Family member not found in database. This may be a mock family member for visualization purposes.');
          } else {
            const errorMessage = t('profile.errors.loadFailed', { defaultValue: 'Failed to load family member details' });
            setError(errorMessage);
            showError(errorMessage);
          }
        }
      }
    } catch (err: any) {
      console.error('Failed to load family member:', err);
      const errorMessage = t('profile.errors.loadFailed', { defaultValue: 'Failed to load family member details' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceBadge = (confidence?: number) => {
    if (!confidence) return null;
    if (confidence >= 95) {
      return <Chip icon={<CheckCircleIcon />} label={`${confidence}%`} color="success" size="small" />;
    } else if (confidence >= 80) {
      return <Chip icon={<WarningIcon />} label={`${confidence}%`} color="warning" size="small" />;
    } else {
      return <Chip label={`${confidence}%`} color="error" size="small" />;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Not provided';
    try {
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '50vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            {t('profile.loadingFamilyMember')}
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error || !member) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error || t('profile.familyMemberNotFound')}
        </Alert>
        <Button
          component={Link}
          to="/profile/dashboard"
          startIcon={<ArrowBackIcon />}
          variant="outlined"
        >
          {t('profile.backToProfileDashboard')}
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Button
          component={Link}
          to="/profile/dashboard"
          startIcon={<ArrowBackIcon />}
          variant="outlined"
          sx={{ mb: 2 }}
        >
          {t('profile.backToProfileDashboard')}
        </Button>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {getUserName({ fullName: member.name, fullNameHindi: undefined }, currentLanguage)}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {t('profile.familyMemberProfile')}
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Profile Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 2 }}>
                <Avatar
                  sx={{
                    width: 120,
                    height: 120,
                    bgcolor: 'primary.main',
                    fontSize: '3rem',
                    mb: 2,
                  }}
                >
                  {member.name.charAt(0).toUpperCase()}
                </Avatar>
                <Typography variant="h5" component="h2" gutterBottom>
                  {getUserName({ fullName: member.name, fullNameHindi: undefined }, currentLanguage)}
                </Typography>
                <Chip label={translateRelationship(member.relationship, t)} color="primary" sx={{ mb: 1 }} />
                {getConfidenceBadge(member.confidence)}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Personal Details */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                {t('profile.personalDetails')}
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <List>
                <ListItem>
                  <ListItemIcon>
                    <PersonIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={t('profile.fullName')}
                    secondary={member.name || t('profile.notProvided')}
                  />
                </ListItem>

                {member.relationship && (
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.relationship')}
                      secondary={translateRelationship(member.relationship, t)}
                    />
                  </ListItem>
                )}

                {member.age && (
                  <ListItem>
                    <ListItemIcon>
                      <CalendarIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.age')}
                      secondary={`${member.age} ${t('profile.years')}`}
                    />
                  </ListItem>
                )}

                {member.dateOfBirth && (
                  <ListItem>
                    <ListItemIcon>
                      <CalendarIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.dateOfBirth')}
                      secondary={formatDate(member.dateOfBirth)}
                    />
                  </ListItem>
                )}

                {member.gender && (
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.gender')}
                      secondary={member.gender}
                    />
                  </ListItem>
                )}

                {member.aadhaarNumber && (
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.aadhaarNumber')}
                      secondary={
                        member.aadhaarNumber.length >= 12
                          ? `${member.aadhaarNumber.substring(0, 4)} **** **** ${member.aadhaarNumber.substring(member.aadhaarNumber.length - 4)}`
                          : member.aadhaarNumber
                      }
                    />
                  </ListItem>
                )}

                {member.mobileNumber && (
                  <ListItem>
                    <ListItemIcon>
                      <PhoneIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.mobileNumber')}
                      secondary={member.mobileNumber}
                    />
                  </ListItem>
                )}

                {member.incomeBand && (
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.incomeBand')}
                      secondary={member.incomeBand}
                    />
                  </ListItem>
                )}

                {member.vulnerabilityCategory && (
                  <ListItem>
                    <ListItemIcon>
                      <PersonIcon color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('profile.vulnerabilityCategory')}
                      secondary={member.vulnerabilityCategory}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

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

