import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  Divider,
  Badge,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  InputAdornment,
} from '@mui/material';
import {
  Send as SendIcon,
  AttachFile as AttachFileIcon,
  Close as CloseIcon,
  Chat as ChatIcon,
  Person as PersonIcon,
  CheckCircle as ResolvedIcon,
  HourglassEmpty as PendingIcon,
  Cancel as CancelledIcon,
  Assignment as InProgressIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useAppSelector } from '@/store/hooks';
import { chatService, ChatConversation, ChatMessage, CreateConversationRequest } from '@/services/chat.service';
import { useWebSocket } from '@/hooks/useWebSocket';
import { useMessageDialog } from '@/hooks/useMessageDialog';
import { MessageDialog } from '@/components/common/MessageDialog';
import { formatDistanceToNow } from 'date-fns';

export const ChatPage: React.FC = () => {
  const { t } = useTranslation();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const { dialog, showSuccess, showError, close } = useMessageDialog();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<ChatConversation | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [messageText, setMessageText] = useState('');
  const [sending, setSending] = useState(false);
  const [newConversationDialog, setNewConversationDialog] = useState(false);
  const [newConversationData, setNewConversationData] = useState<CreateConversationRequest>({
    subject: '',
    message: '',
    priority: 'MEDIUM',
    category: '',
  });
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);

  // WebSocket for real-time messages
  const { isConnected, sendMessage } = useWebSocket({
    topics: selectedConversation
      ? [`/queue/citizen/${user?.id}/chat/${selectedConversation.id}`]
      : [],
    onMessage: (message: ChatMessage) => {
      if (message.conversationId === selectedConversation?.id) {
        setMessages((prev) => {
          // Avoid duplicates
          if (prev.some((m) => m.id === message.id)) {
            return prev;
          }
          return [...prev, message];
        });
        // Mark as read if it's from an agent
        if (message.senderType === 'AGENT' && !message.read) {
          chatService.markAsRead(selectedConversation.id, [message.id]).catch(console.error);
        }
      } else {
        // Update conversation list if message is for another conversation
        loadConversations();
      }
    },
    onError: (err) => {
      console.error('WebSocket error:', err);
    },
    autoConnect: !!selectedConversation && isAuthenticated,
  });

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      loadConversations();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user?.id]);

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation.id, 0);
      setPage(0);
      setHasMore(true);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    if (!user?.id) return;

    try {
      setLoading(true);
      setError(null);
      const response = await chatService.getConversations(user.id, 0, 50);
      setConversations(response.content || []);
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
      const errorMessage = err.response?.data?.message || t('chat.loadFailed', { defaultValue: 'Failed to load conversations' });
      setError(errorMessage);
      showError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (conversationId: string, pageNum: number) => {
    try {
      const response = await chatService.getMessages(conversationId, pageNum, 50);
      const newMessages = response.content || [];
      
      if (pageNum === 0) {
        setMessages(newMessages.reverse()); // Reverse to show oldest first
      } else {
        setMessages((prev) => [...newMessages.reverse(), ...prev]);
      }
      
      setHasMore(!response.last);
      
      // Mark messages as read
      const unreadIds = newMessages
        .filter((m) => !m.read && m.senderType === 'AGENT')
        .map((m) => m.id);
      if (unreadIds.length > 0) {
        await chatService.markAsRead(conversationId, unreadIds);
      }
    } catch (err: any) {
      console.error('Failed to load messages:', err);
      showError(err.response?.data?.message || t('chat.messagesLoadFailed', { defaultValue: 'Failed to load messages' }));
    }
  };

  const handleSendMessage = async () => {
    if (!messageText.trim() || !selectedConversation || sending) return;

    try {
      setSending(true);
      const newMessage = await chatService.sendMessage(selectedConversation.id, {
        message: messageText.trim(),
      });
      
      setMessages((prev) => [...prev, newMessage]);
      setMessageText('');
      
      // Send via WebSocket for real-time delivery
      if (isConnected) {
        sendMessage(`/app/chat/${selectedConversation.id}/send`, {
          message: messageText.trim(),
        });
      }
    } catch (err: any) {
      console.error('Failed to send message:', err);
      showError(err.response?.data?.message || t('chat.sendFailed', { defaultValue: 'Failed to send message' }));
    } finally {
      setSending(false);
    }
  };

  const handleCreateConversation = async () => {
    if (!user?.id || !newConversationData.subject.trim() || !newConversationData.message.trim()) {
      showError(t('chat.fillAllFields', { defaultValue: 'Please fill all required fields' }));
      return;
    }

    try {
      const conversation = await chatService.createConversation(user.id, newConversationData);
      setConversations((prev) => [conversation, ...prev]);
      setSelectedConversation(conversation);
      setNewConversationDialog(false);
      setNewConversationData({ subject: '', message: '', priority: 'MEDIUM', category: '' });
      showSuccess(t('chat.conversationCreated', { defaultValue: 'Conversation created successfully' }));
    } catch (err: any) {
      console.error('Failed to create conversation:', err);
      showError(err.response?.data?.message || t('chat.createFailed', { defaultValue: 'Failed to create conversation' }));
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return <ResolvedIcon color="success" fontSize="small" />;
      case 'IN_PROGRESS':
        return <InProgressIcon color="info" fontSize="small" />;
      case 'CLOSED':
        return <CancelledIcon color="default" fontSize="small" />;
      default:
        return <PendingIcon color="warning" fontSize="small" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'RESOLVED':
        return 'success';
      case 'IN_PROGRESS':
        return 'info';
      case 'CLOSED':
        return 'default';
      default:
        return 'warning';
    }
  };

  const formatMessageTime = (timestamp: string) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
    } catch {
      return timestamp;
    }
  };

  if (!isAuthenticated) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Alert severity="warning">
          {t('chat.loginRequired', { defaultValue: 'Please log in to access chat support.' })}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4, height: 'calc(100vh - 200px)' }}>
      <Box sx={{ display: 'flex', gap: 2, height: '100%' }}>
        {/* Conversations List */}
        <Paper sx={{ width: 350, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">{t('chat.conversations', { defaultValue: 'Conversations' })}</Typography>
            <Button
              variant="contained"
              size="small"
              startIcon={<ChatIcon />}
              onClick={() => setNewConversationDialog(true)}
            >
              {t('chat.new', { defaultValue: 'New' })}
            </Button>
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          ) : conversations.length === 0 ? (
            <Box sx={{ textAlign: 'center', p: 4 }}>
              <ChatIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="body2" color="text.secondary">
                {t('chat.noConversations', { defaultValue: 'No conversations yet. Start a new conversation to get help.' })}
              </Typography>
            </Box>
          ) : (
            <List sx={{ flexGrow: 1, overflow: 'auto' }}>
              {conversations.map((conversation) => (
                <ListItem
                  key={conversation.id}
                  button
                  selected={selectedConversation?.id === conversation.id}
                  onClick={() => setSelectedConversation(conversation)}
                  sx={{
                    borderLeft: selectedConversation?.id === conversation.id ? 3 : 0,
                    borderColor: 'primary.main',
                  }}
                >
                  <ListItemAvatar>
                    <Badge badgeContent={conversation.unreadCount} color="primary">
                      <Avatar>
                        <PersonIcon />
                      </Avatar>
                    </Badge>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                        <Typography variant="subtitle2" noWrap sx={{ flexGrow: 1 }}>
                          {conversation.subject || t('chat.noSubject', { defaultValue: 'No Subject' })}
                        </Typography>
                        <Chip
                          label={conversation.status}
                          size="small"
                          color={getStatusColor(conversation.status) as any}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        {conversation.lastMessage && (
                          <Typography variant="body2" color="text.secondary" noWrap>
                            {conversation.lastMessage.message}
                          </Typography>
                        )}
                        <Typography variant="caption" color="text.secondary">
                          {conversation.lastMessage
                            ? formatMessageTime(conversation.lastMessage.timestamp)
                            : formatMessageTime(conversation.createdAt)}
                        </Typography>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          )}
        </Paper>

        {/* Chat Area */}
        <Paper sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {selectedConversation ? (
            <>
              {/* Chat Header */}
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="h6">{selectedConversation.subject || t('chat.noSubject', { defaultValue: 'No Subject' })}</Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                    {getStatusIcon(selectedConversation.status)}
                    <Chip
                      label={selectedConversation.status}
                      size="small"
                      color={getStatusColor(selectedConversation.status) as any}
                    />
                    <Chip label={selectedConversation.priority} size="small" variant="outlined" />
                  </Box>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {isConnected ? (
                    <Chip label={t('chat.connected', { defaultValue: 'Connected' })} color="success" size="small" />
                  ) : (
                    <Chip label={t('chat.connecting', { defaultValue: 'Connecting...' })} color="warning" size="small" />
                  )}
                </Box>
              </Box>

              {/* Messages */}
              <Box sx={{ flexGrow: 1, overflow: 'auto', p: 2, bgcolor: 'grey.50' }}>
                {messages.length === 0 ? (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <Typography variant="body2" color="text.secondary">
                      {t('chat.noMessages', { defaultValue: 'No messages yet. Start the conversation!' })}
                    </Typography>
                  </Box>
                ) : (
                  <>
                    {messages.map((message) => (
                      <Box
                        key={message.id}
                        sx={{
                          display: 'flex',
                          justifyContent: message.senderType === 'CITIZEN' ? 'flex-end' : 'flex-start',
                          mb: 2,
                        }}
                      >
                        <Paper
                          elevation={1}
                          sx={{
                            p: 1.5,
                            maxWidth: '70%',
                            bgcolor: message.senderType === 'CITIZEN' ? 'primary.main' : 'background.paper',
                            color: message.senderType === 'CITIZEN' ? 'primary.contrastText' : 'text.primary',
                          }}
                        >
                          <Typography variant="body2">{message.message}</Typography>
                          <Typography
                            variant="caption"
                            sx={{
                              display: 'block',
                              mt: 0.5,
                              opacity: 0.7,
                            }}
                          >
                            {formatMessageTime(message.timestamp)}
                            {message.read && message.senderType === 'CITIZEN' && ' ✓'}
                          </Typography>
                        </Paper>
                      </Box>
                    ))}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </Box>

              {/* Message Input */}
              <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <TextField
                    fullWidth
                    multiline
                    maxRows={4}
                    placeholder={t('chat.typeMessage', { defaultValue: 'Type your message...' })}
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage();
                      }
                    }}
                    disabled={sending || !isConnected}
                  />
                  <IconButton color="primary" disabled={sending || !isConnected}>
                    <AttachFileIcon />
                  </IconButton>
                  <Button
                    variant="contained"
                    endIcon={<SendIcon />}
                    onClick={handleSendMessage}
                    disabled={!messageText.trim() || sending || !isConnected}
                  >
                    {sending ? <CircularProgress size={20} /> : t('chat.send', { defaultValue: 'Send' })}
                  </Button>
                </Box>
              </Box>
            </>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', p: 4 }}>
              <ChatIcon sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {t('chat.selectConversation', { defaultValue: 'Select a conversation' })}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('chat.selectOrCreate', { defaultValue: 'Select an existing conversation or create a new one to start chatting.' })}
              </Typography>
            </Box>
          )}
        </Paper>
      </Box>

      {/* New Conversation Dialog */}
      <Dialog open={newConversationDialog} onClose={() => setNewConversationDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {t('chat.newConversation', { defaultValue: 'New Conversation' })}
          <IconButton
            aria-label="close"
            onClick={() => setNewConversationDialog(false)}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              fullWidth
              label={t('chat.subject', { defaultValue: 'Subject' })}
              value={newConversationData.subject}
              onChange={(e) => setNewConversationData((prev) => ({ ...prev, subject: e.target.value }))}
              required
            />
            <FormControl fullWidth>
              <InputLabel>{t('chat.priority', { defaultValue: 'Priority' })}</InputLabel>
              <Select
                value={newConversationData.priority}
                onChange={(e) => setNewConversationData((prev) => ({ ...prev, priority: e.target.value as any }))}
                label={t('chat.priority', { defaultValue: 'Priority' })}
              >
                <MenuItem value="LOW">{t('chat.priority.low', { defaultValue: 'Low' })}</MenuItem>
                <MenuItem value="MEDIUM">{t('chat.priority.medium', { defaultValue: 'Medium' })}</MenuItem>
                <MenuItem value="HIGH">{t('chat.priority.high', { defaultValue: 'High' })}</MenuItem>
                <MenuItem value="URGENT">{t('chat.priority.urgent', { defaultValue: 'Urgent' })}</MenuItem>
              </Select>
            </FormControl>
            <TextField
              fullWidth
              multiline
              rows={6}
              label={t('chat.message', { defaultValue: 'Message' })}
              value={newConversationData.message}
              onChange={(e) => setNewConversationData((prev) => ({ ...prev, message: e.target.value }))}
              required
              placeholder={t('chat.messagePlaceholder', { defaultValue: 'Describe your issue or question...' })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewConversationDialog(false)}>
            {t('common.cancel', { defaultValue: 'Cancel' })}
          </Button>
          <Button
            variant="contained"
            onClick={handleCreateConversation}
            disabled={!newConversationData.subject.trim() || !newConversationData.message.trim()}
          >
            {t('chat.start', { defaultValue: 'Start Conversation' })}
          </Button>
        </DialogActions>
      </Dialog>

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

