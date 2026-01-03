package com.smart.citizen.repository;

import com.smart.citizen.entity.ChatConversation;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ChatConversationRepository extends JpaRepository<ChatConversation, UUID> {

    Page<ChatConversation> findByCitizenIdOrderByLastMessageAtDesc(UUID citizenId, Pageable pageable);

    List<ChatConversation> findByCitizenIdOrderByLastMessageAtDesc(UUID citizenId);

    List<ChatConversation> findByCitizenIdAndStatus(UUID citizenId, ChatConversation.ConversationStatus status);

    @Query("SELECT COUNT(c) FROM ChatConversation c WHERE c.citizen.id = :citizenId AND c.status IN :statuses")
    Long countByCitizenIdAndStatusIn(@Param("citizenId") UUID citizenId, 
                                     @Param("statuses") List<ChatConversation.ConversationStatus> statuses);

    @Query("SELECT c FROM ChatConversation c WHERE c.citizen.id = :citizenId " +
           "AND (c.status = 'OPEN' OR c.status = 'IN_PROGRESS') " +
           "ORDER BY c.lastMessageAt DESC")
    List<ChatConversation> findActiveConversationsByCitizenId(@Param("citizenId") UUID citizenId);
}

