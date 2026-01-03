import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  MenuItem,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Edit as EditIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Home as HomeIcon,
  CalendarToday as CalendarIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { RootState } from '@/store';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { citizenService } from '@/services/citizen.service';
import { fetchCurrentUser } from '@/store/slices/auth.slice';
import { CitizenRequest, CitizenUpdateRequest, User } from '@/types/api';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { getUsernameFromToken } from '@/utils/jwt';

export const ProfilePage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, token, profileNotFound } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();

  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<CitizenRequest | CitizenUpdateRequest>({
    fullName: '',
    email: '',
    mobileNumber: '',
    aadhaarNumber: '',
    dateOfBirth: '',
    gender: undefined,
    addressLine1: '',
    addressLine2: '',
    city: '',
    district: '',
    pincode: '',
  });

  // Get Aadhaar number from JWT token
  const aadhaarNumber = token ? getUsernameFromToken(token) : null;

  useEffect(() => {
    if (isAuthenticated) {
      if (user?.id) {
        // User profile exists - load it and set edit mode
        loadProfile();
        setIsEditing(false);
      } else {
        // Profile doesn't exist - set create mode
        setIsEditing(true);
        // Pre-fill Aadhaar number from token if available
        if (aadhaarNumber) {
          setFormData((prev) => ({ ...prev, aadhaarNumber }));
        }
      }
    }
  }, [isAuthenticated, user?.id, aadhaarNumber]);

  const loadProfile = async () => {
    if (!user?.id) return;

    setLoading(true);
    setError(null);
    try {
      const profile = await citizenService.getCitizenById(user.id);
      setFormData({
        fullName: profile.fullName || '',
        email: profile.email || '',
        mobileNumber: profile.mobileNumber || '',
        dateOfBirth: profile.dateOfBirth || '',
        gender: profile.gender,
        addressLine1: profile.addressLine1 || '',
        addressLine2: profile.addressLine2 || '',
        city: profile.city || '',
        district: profile.district || '',
        pincode: profile.pincode || '',
      });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = async () => {
    setError(null);

    // Validation
    if (!formData.fullName?.trim()) {
      setError('Full name is required');
      return;
    }
    if (!formData.mobileNumber?.trim()) {
      setError('Mobile number is required');
      return;
    }
    if (formData.mobileNumber && !/^[0-9]{10}$/.test(formData.mobileNumber)) {
      setError('Mobile number must be 10 digits');
      return;
    }
    if (formData.pincode && !/^[0-9]{6}$/.test(formData.pincode)) {
      setError('Pincode must be 6 digits');
      return;
    }
    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError('Please enter a valid email address');
      return;
    }

    setSaving(true);
    try {
      if (user?.id) {
        // Update existing profile
        const updateData: CitizenUpdateRequest = {
          fullName: formData.fullName,
          email: formData.email,
          dateOfBirth: formData.dateOfBirth,
          gender: formData.gender,
          addressLine1: formData.addressLine1,
          addressLine2: formData.addressLine2,
          city: formData.city,
          district: formData.district,
          pincode: formData.pincode,
        };
        await citizenService.updateCitizen(user.id, updateData);
        showSuccess(t('profile.updateSuccess', { defaultValue: 'Profile updated successfully' }));
      } else {
        // Create new profile
        const createData: CitizenRequest = {
          fullName: formData.fullName!,
          mobileNumber: formData.mobileNumber!,
          aadhaarNumber: aadhaarNumber || formData.aadhaarNumber,
          email: formData.email,
          dateOfBirth: formData.dateOfBirth,
          gender: formData.gender,
          addressLine1: formData.addressLine1,
          addressLine2: formData.addressLine2,
          city: formData.city,
          district: formData.district,
          pincode: formData.pincode,
        };
        await citizenService.createCitizen(createData);
        showSuccess(t('profile.createSuccess', { defaultValue: 'Profile created successfully' }));
      }

      // Refresh user profile
      await dispatch(fetchCurrentUser()).unwrap();
      setIsEditing(false);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || t('profile.saveError', { defaultValue: 'Failed to save profile' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    if (user?.id) {
      // Reload profile data
      loadProfile();
      setIsEditing(false);
    } else {
      // Clear form if creating new profile
      setFormData({
        fullName: '',
        email: '',
        mobileNumber: '',
        aadhaarNumber: aadhaarNumber || '',
        dateOfBirth: '',
        gender: undefined,
        addressLine1: '',
        addressLine2: '',
        city: '',
        district: '',
        pincode: '',
      });
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">Please log in to view your profile</Alert>
      </Container>
    );
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          {user?.id ? 'My Profile' : 'Complete Your Profile'}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {user?.id
            ? 'View and update your personal information'
            : 'Please complete your profile to access all features'}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!user?.id && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Your profile needs to be created. Please fill in the required information below.
        </Alert>
      )}

      <Paper elevation={2} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" component="h2">
            Personal Information
          </Typography>
          {user?.id && !isEditing && (
            <Button
              variant="outlined"
              startIcon={<EditIcon />}
              onClick={() => setIsEditing(true)}
            >
              Edit Profile
            </Button>
          )}
        </Box>

        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          {/* Full Name */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Full Name"
              required
              value={formData.fullName || ''}
              onChange={(e) => handleInputChange('fullName', e.target.value)}
              disabled={!isEditing}
              InputProps={{
                startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Mobile Number */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Mobile Number"
              required
              value={formData.mobileNumber || ''}
              onChange={(e) => handleInputChange('mobileNumber', e.target.value.replace(/\D/g, '').slice(0, 10))}
              disabled={!isEditing || !!user?.id} // Can't change mobile if profile exists
              helperText={user?.id ? 'Mobile number cannot be changed' : '10-digit mobile number'}
              InputProps={{
                startAdornment: <PhoneIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Aadhaar Number */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Aadhaar Number"
              value={aadhaarNumber || formData.aadhaarNumber || ''}
              disabled
              helperText="Aadhaar number is linked to your account"
              InputProps={{
                startAdornment: <PersonIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Email */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={formData.email || ''}
              onChange={(e) => handleInputChange('email', e.target.value)}
              disabled={!isEditing}
              InputProps={{
                startAdornment: <EmailIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Date of Birth */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Date of Birth"
              type="date"
              value={formData.dateOfBirth || ''}
              onChange={(e) => handleInputChange('dateOfBirth', e.target.value)}
              disabled={!isEditing}
              InputLabelProps={{ shrink: true }}
              InputProps={{
                startAdornment: <CalendarIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Gender */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              select
              label="Gender"
              value={formData.gender || ''}
              onChange={(e) => handleInputChange('gender', e.target.value)}
              disabled={!isEditing}
            >
              <MenuItem value="">Select Gender</MenuItem>
              <MenuItem value="MALE">Male</MenuItem>
              <MenuItem value="FEMALE">Female</MenuItem>
              <MenuItem value="OTHER">Other</MenuItem>
            </TextField>
          </Grid>

          {/* Address Line 1 */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address Line 1"
              value={formData.addressLine1 || ''}
              onChange={(e) => handleInputChange('addressLine1', e.target.value)}
              disabled={!isEditing}
              InputProps={{
                startAdornment: <HomeIcon sx={{ mr: 1, color: 'action.active' }} />,
              }}
            />
          </Grid>

          {/* Address Line 2 */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Address Line 2"
              value={formData.addressLine2 || ''}
              onChange={(e) => handleInputChange('addressLine2', e.target.value)}
              disabled={!isEditing}
            />
          </Grid>

          {/* City */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="City"
              value={formData.city || ''}
              onChange={(e) => handleInputChange('city', e.target.value)}
              disabled={!isEditing}
            />
          </Grid>

          {/* District */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="District"
              value={formData.district || ''}
              onChange={(e) => handleInputChange('district', e.target.value)}
              disabled={!isEditing}
            />
          </Grid>

          {/* Pincode */}
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Pincode"
              value={formData.pincode || ''}
              onChange={(e) => handleInputChange('pincode', e.target.value.replace(/\D/g, '').slice(0, 6))}
              disabled={!isEditing}
              helperText="6-digit pincode"
            />
          </Grid>
        </Grid>

        {isEditing && (
          <Box sx={{ display: 'flex', gap: 2, mt: 4, justifyContent: 'flex-end' }}>
            <Button variant="outlined" onClick={handleCancel} disabled={saving}>
              Cancel
            </Button>
            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Saving...' : user?.id ? 'Update Profile' : 'Create Profile'}
            </Button>
          </Box>
        )}
      </Paper>

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

export default ProfilePage;

