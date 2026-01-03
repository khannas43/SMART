package com.smart.citizen.repository;

import com.smart.citizen.entity.ChatMessage;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, UUID> {

    Page<ChatMessage> findByConversationIdOrderByCreatedAtAsc(UUID conversationId, Pageable pageable);

    List<ChatMessage> findByConversationIdOrderByCreatedAtAsc(UUID conversationId);

    @Query("SELECT m FROM ChatMessage m WHERE m.conversation.id = :conversationId ORDER BY m.createdAt DESC")
    Page<ChatMessage> findByConversationIdOrderByCreatedAtDesc(@Param("conversationId") UUID conversationId, Pageable pageable);

    @Query("SELECT COUNT(m) FROM ChatMessage m WHERE m.conversation.id = :conversationId AND m.isRead = false AND m.senderType != 'CITIZEN'")
    Long countUnreadMessagesByConversationId(@Param("conversationId") UUID conversationId);

    @Query("SELECT COUNT(m) FROM ChatMessage m " +
           "JOIN m.conversation c " +
           "WHERE c.citizen.id = :citizenId AND m.isRead = false AND m.senderType != 'CITIZEN'")
    Long countUnreadMessagesByCitizenId(@Param("citizenId") UUID citizenId);

    @Query("SELECT m FROM ChatMessage m WHERE m.conversation.id = :conversationId AND m.isRead = false AND m.senderType != 'CITIZEN'")
    List<ChatMessage> findUnreadMessagesByConversationId(@Param("conversationId") UUID conversationId);
}

