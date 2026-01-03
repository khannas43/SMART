import { useState } from 'react';
import { MessageType } from '@/components/common/MessageDialog';

interface MessageDialogState {
  open: boolean;
  type: MessageType;
  message: string;
  title?: string;
}

export const useMessageDialog = () => {
  const [dialog, setDialog] = useState<MessageDialogState>({
    open: false,
    type: 'info',
    message: '',
  });

  const showSuccess = (message: string, title?: string) => {
    setDialog({ open: true, type: 'success', message, title });
  };

  const showError = (message: string, title?: string) => {
    setDialog({ open: true, type: 'error', message, title });
  };

  const showWarning = (message: string, title?: string) => {
    setDialog({ open: true, type: 'warning', message, title });
  };

  const showInfo = (message: string, title?: string) => {
    setDialog({ open: true, type: 'info', message, title });
  };

  const close = () => {
    setDialog({ open: false, type: 'info', message: '' });
  };

  return {
    dialog,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    close,
  };
};

