import React from 'react';
import { useTranslation } from 'react-i18next';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  IconButton,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

export type MessageType = 'success' | 'error' | 'info' | 'warning';

interface MessageDialogProps {
  open: boolean;
  onClose: () => void;
  type: MessageType;
  title?: string;
  message: string;
  autoClose?: boolean;
  autoCloseDelay?: number;
}

export const MessageDialog: React.FC<MessageDialogProps> = ({
  open,
  onClose,
  type,
  title,
  message,
  autoClose = false,
  autoCloseDelay = 3000,
}) => {
  const { t } = useTranslation();
  React.useEffect(() => {
    if (open && autoClose && type === 'success') {
      const timer = setTimeout(() => {
        onClose();
      }, autoCloseDelay);
      return () => clearTimeout(timer);
    }
  }, [open, autoClose, autoCloseDelay, type, onClose]);

  const getIcon = () => {
    const iconStyle = { fontSize: 48, mb: 2 };
    switch (type) {
      case 'success':
        return <SuccessIcon color="success" sx={iconStyle} />;
      case 'error':
        return <ErrorIcon color="error" sx={iconStyle} />;
      case 'warning':
        return <WarningIcon color="warning" sx={iconStyle} />;
      case 'info':
        return <InfoIcon color="info" sx={iconStyle} />;
      default:
        return <InfoIcon color="info" sx={iconStyle} />;
    }
  };

  const getDefaultTitle = () => {
    switch (type) {
      case 'success':
        return t('common.success', { defaultValue: 'Success' });
      case 'error':
        return t('common.error', { defaultValue: 'Error' });
      case 'warning':
        return t('common.warning', { defaultValue: 'Warning' });
      case 'info':
        return t('common.information', { defaultValue: 'Information' });
      default:
        return t('common.message', { defaultValue: 'Message' });
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
          textAlign: 'center',
        },
      }}
    >
      <DialogTitle sx={{ pb: 1, position: 'relative' }}>
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent sx={{ pt: 2, pb: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          {getIcon()}
          <Typography variant="h6" component="div" gutterBottom fontWeight="bold">
            {title || getDefaultTitle()}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {message}
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions sx={{ justifyContent: 'center', pb: 3 }}>
        <Button onClick={onClose} variant="contained" color="primary" sx={{ minWidth: 100 }}>
          {t('common.ok', { defaultValue: 'OK' })}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

