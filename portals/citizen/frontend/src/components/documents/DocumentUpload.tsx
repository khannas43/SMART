import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Button,
  TextField,
  Typography,
  Alert,
  CircularProgress,
  MenuItem,
  Paper,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { documentService } from '@/services/document.service';
import { MessageDialog, MessageType } from '@/components/common/MessageDialog';

interface DocumentUploadProps {
  citizenId: string;
  applicationId?: string;
  onUploadSuccess?: () => void;
  documentTypes?: string[];
}

const DEFAULT_DOCUMENT_TYPES = [
  'AADHAAR',
  'PAN',
  'INCOME_CERTIFICATE',
  'ADDRESS_PROOF',
  'BIRTH_CERTIFICATE',
  'EDUCATION_CERTIFICATE',
  'DISABILITY_CERTIFICATE',
  'CASTE_CERTIFICATE',
  'PHOTO',
  'SIGNATURE',
  'OTHER',
];

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  citizenId,
  applicationId,
  onUploadSuccess,
  documentTypes = DEFAULT_DOCUMENT_TYPES,
}) => {
  const { t } = useTranslation();
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [messageDialog, setMessageDialog] = useState<{
    open: boolean;
    type: MessageType;
    message: string;
  }>({ open: false, type: 'info', message: '' });

  // Helper function to get translated document type name
  const getDocumentTypeLabel = (type: string): string => {
    const key = `documents.types.${type.toLowerCase()}`;
    const translated = t(key, { defaultValue: type.replace(/_/g, ' ') });
    return translated;
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      // Validate file size (10MB max)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setMessageDialog({
          open: true,
          type: 'error',
          message: t('documents.errors.fileSizeTooLarge', { defaultValue: 'File size must be less than 10MB' }),
        });
        return;
      }
      setFile(selectedFile);
      setUploadSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !documentType) {
      setMessageDialog({
        open: true,
        type: 'error',
        message: t('documents.errors.selectFileAndType', { defaultValue: 'Please select a file and document type' }),
      });
      return;
    }

    // Validate citizenId is a valid UUID
    const isValidUUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(citizenId);
    if (!isValidUUID) {
      setMessageDialog({
        open: true,
        type: 'error',
        message: t('documents.errors.invalidUserId', { defaultValue: 'Invalid user ID. Please log in again.' }),
      });
      return;
    }

    setUploading(true);
    try {
      await documentService.uploadDocument(citizenId, file, documentType, applicationId);
      setMessageDialog({
        open: true,
        type: 'success',
        message: t('documents.uploadSuccess', { defaultValue: 'Document uploaded successfully' }),
      });
      setUploadSuccess(true);
      setFile(null);
      setDocumentType('');
      if (onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (error: any) {
      setMessageDialog({
        open: true,
        type: 'error',
        message: error.response?.data?.message || t('documents.errors.uploadFailed', { defaultValue: 'Failed to upload document' }),
      });
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {t('documents.uploadTitle', { defaultValue: 'Upload Document' })}
      </Typography>

      {uploadSuccess && (
        <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircleIcon />}>
          {t('documents.uploadSuccess', { defaultValue: 'Document uploaded successfully!' })}
        </Alert>
      )}

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          select
          label={t('documents.documentType', { defaultValue: 'Document Type' })}
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          fullWidth
          required
        >
          {documentTypes.map((type) => (
            <MenuItem key={type} value={type}>
              {getDocumentTypeLabel(type)}
            </MenuItem>
          ))}
        </TextField>

        <Box>
          <input
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            style={{ display: 'none' }}
            id="document-upload-input"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="document-upload-input">
            <Button
              variant="outlined"
              component="span"
              startIcon={<CloudUploadIcon />}
              fullWidth
              sx={{ py: 1.5 }}
            >
              {file ? file.name : t('documents.chooseFile', { defaultValue: 'Choose File' })}
            </Button>
          </label>
          {file && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              {t('documents.fileSize', { defaultValue: 'Size' })}: {formatFileSize(file.size)}
            </Typography>
          )}
        </Box>

        <Button
          variant="contained"
          onClick={handleUpload}
          disabled={!file || !documentType || uploading}
          startIcon={uploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
          fullWidth
        >
          {uploading ? t('documents.uploading', { defaultValue: 'Uploading...' }) : t('documents.uploadButton', { defaultValue: 'Upload Document' })}
        </Button>
      </Box>

      {/* Message Dialog */}
      <MessageDialog
        open={messageDialog.open}
        onClose={() => setMessageDialog({ open: false, type: 'info', message: '' })}
        type={messageDialog.type}
        message={messageDialog.message}
        autoClose={messageDialog.type === 'success'}
        autoCloseDelay={3000}
      />
    </Paper>
  );
};

