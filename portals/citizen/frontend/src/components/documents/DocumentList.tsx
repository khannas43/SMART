import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Card,
  CardContent,
  Typography,
  IconButton,
  Chip,
  Tooltip,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Verified as VerifiedIcon,
  Pending as PendingIcon,
  Cancel as RejectedIcon,
} from '@mui/icons-material';
import { Document } from '@/types/api';
import { documentService } from '@/services/document.service';
import { MessageDialog, MessageType } from '@/components/common/MessageDialog';

interface DocumentListProps {
  documents: Document[];
  onDelete?: () => void;
  showActions?: boolean;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onDelete,
  showActions = true,
}) => {
  const { t } = useTranslation();
  const [messageDialog, setMessageDialog] = useState<{
    open: boolean;
    type: MessageType;
    message: string;
  }>({ open: false, type: 'info', message: '' });
  const [deleteDialog, setDeleteDialog] = useState<{
    open: boolean;
    documentId: string | null;
  }>({ open: false, documentId: null });

  // Helper function to get translated document type name
  const getDocumentTypeLabel = (type: string): string => {
    if (!type) return t('documents.types.other', { defaultValue: 'Document' });
    const key = `documents.types.${type.toLowerCase()}`;
    const translated = t(key, { defaultValue: type.replace(/_/g, ' ') });
    return translated;
  };

  // Helper function to get translated status label
  const getStatusLabel = (status: string): string => {
    if (!status) return t('documents.status.pending', { defaultValue: 'PENDING' });
    const key = `documents.status.${status.toLowerCase()}`;
    const translated = t(key, { defaultValue: status });
    return translated;
  };
  const getStatusColor = (status: string): 'default' | 'success' | 'warning' | 'error' => {
    switch (status?.toUpperCase()) {
      case 'VERIFIED':
        return 'success';
      case 'PENDING':
        return 'warning';
      case 'REJECTED':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'VERIFIED':
        return <VerifiedIcon fontSize="small" />;
      case 'PENDING':
        return <PendingIcon fontSize="small" />;
      case 'REJECTED':
        return <RejectedIcon fontSize="small" />;
      default:
        return null;
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await documentService.downloadDocument(doc.id);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = doc.documentName || doc.fileName || `document-${doc.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setMessageDialog({
        open: true,
        type: 'success',
        message: t('documents.downloadSuccess', { defaultValue: 'Document downloaded' }),
      });
    } catch (error: any) {
      setMessageDialog({
        open: true,
        type: 'error',
        message: error.response?.data?.message || t('documents.downloadFailed', { defaultValue: 'Failed to download document' }),
      });
    }
  };

  const handleDeleteClick = (documentId: string) => {
    setDeleteDialog({ open: true, documentId });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteDialog.documentId) return;

    try {
      await documentService.deleteDocument(deleteDialog.documentId);
      setDeleteDialog({ open: false, documentId: null });
      setMessageDialog({
        open: true,
        type: 'success',
        message: t('documents.deleteSuccess', { defaultValue: 'Document deleted successfully' }),
      });
      if (onDelete) {
        onDelete();
      }
    } catch (error: any) {
      setDeleteDialog({ open: false, documentId: null });
      setMessageDialog({
        open: true,
        type: 'error',
        message: error.response?.data?.message || t('documents.deleteFailed', { defaultValue: 'Failed to delete document' }),
      });
    }
  };

  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '-';
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (documents.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="body2" color="text.secondary">
          {t('documents.noDocuments', { defaultValue: 'No documents found' })}
        </Typography>
      </Box>
    );
  }

  return (
    <>
      <Grid container spacing={2}>
      {documents.map((doc) => (
        <Grid item xs={12} sm={6} md={4} key={doc.id}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1 }}>
                <Box sx={{ flex: 1 }}>
                  <Typography variant="subtitle1" fontWeight="bold" noWrap>
                    {getDocumentTypeLabel(doc.documentType || '')}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {doc.documentName || doc.fileName || t('documents.untitled', { defaultValue: 'Untitled' })}
                  </Typography>
                </Box>
                {showActions && (
                  <Box>
                    <Tooltip title={t('common.download', { defaultValue: 'Download' })}>
                      <IconButton
                        size="small"
                        onClick={() => handleDownload(doc)}
                        color="primary"
                      >
                        <DownloadIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title={t('common.delete', { defaultValue: 'Delete' })}>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteClick(doc.id)}
                        color="error"
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
                )}
              </Box>

              <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Chip
                  label={getStatusLabel(doc.verificationStatus || 'PENDING')}
                  color={getStatusColor(doc.verificationStatus || 'PENDING')}
                  size="small"
                  icon={getStatusIcon(doc.verificationStatus || 'PENDING')}
                  sx={{ alignSelf: 'flex-start' }}
                />
                <Typography variant="caption" color="text.secondary">
                  {t('documents.size', { defaultValue: 'Size' })}: {formatFileSize(doc.fileSize)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {t('documents.uploaded', { defaultValue: 'Uploaded' })}: {formatDate(doc.createdAt)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>

    {/* Delete Confirmation Dialog */}
    <Dialog
      open={deleteDialog.open}
      onClose={() => setDeleteDialog({ open: false, documentId: null })}
    >
      <DialogTitle>{t('common.confirm', { defaultValue: 'Confirm' })}</DialogTitle>
      <DialogContent>
        <DialogContentText>
          {t('documents.deleteConfirm', { defaultValue: 'Are you sure you want to delete this document?' })}
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDeleteDialog({ open: false, documentId: null })}>
          {t('common.cancel', { defaultValue: 'Cancel' })}
        </Button>
        <Button onClick={handleDeleteConfirm} color="error" variant="contained">
          {t('common.delete', { defaultValue: 'Delete' })}
        </Button>
      </DialogActions>
    </Dialog>

    {/* Message Dialog */}
    <MessageDialog
      open={messageDialog.open}
      onClose={() => setMessageDialog({ open: false, type: 'info', message: '' })}
      type={messageDialog.type}
      message={messageDialog.message}
      autoClose={messageDialog.type === 'success'}
      autoCloseDelay={3000}
    />
    </>
  );
};

