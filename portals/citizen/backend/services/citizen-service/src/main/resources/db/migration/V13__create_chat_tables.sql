-- Create chat conversations table
CREATE TABLE IF NOT EXISTS chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citizen_id UUID NOT NULL,
    agent_id UUID,
    subject VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'OPEN',
    priority VARCHAR(50) NOT NULL DEFAULT 'MEDIUM',
    category VARCHAR(100),
    last_message_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT fk_chat_conversation_citizen FOREIGN KEY (citizen_id) REFERENCES citizens(id) ON DELETE CASCADE,
    CONSTRAINT chk_chat_conversation_status CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')),
    CONSTRAINT chk_chat_conversation_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT'))
);

-- Create indexes for chat_conversations
CREATE INDEX IF NOT EXISTS idx_chat_conversation_citizen ON chat_conversations(citizen_id);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_status ON chat_conversations(status);
CREATE INDEX IF NOT EXISTS idx_chat_conversation_created ON chat_conversations(created_at);

-- Create chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    sender_id UUID NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT fk_chat_message_conversation FOREIGN KEY (conversation_id) REFERENCES chat_conversations(id) ON DELETE CASCADE,
    CONSTRAINT chk_chat_message_sender_type CHECK (sender_type IN ('CITIZEN', 'AGENT', 'SYSTEM'))
);

-- Create indexes for chat_messages
CREATE INDEX IF NOT EXISTS idx_chat_message_conversation ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_sender ON chat_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_created ON chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_message_read ON chat_messages(is_read);

-- Add trigger for updated_at on chat_conversations
CREATE TRIGGER update_chat_conversations_updated_at
    BEFORE UPDATE ON chat_conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add trigger for updated_at on chat_messages
CREATE TRIGGER update_chat_messages_updated_at
    BEFORE UPDATE ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

