package com.smart.citizen.repository;

import com.smart.citizen.entity.Feedback;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, UUID> {

    List<Feedback> findByCitizenId(UUID citizenId);

    Page<Feedback> findByCitizenId(UUID citizenId, Pageable pageable);

    List<Feedback> findByApplicationId(UUID applicationId);

    List<Feedback> findByType(Feedback.FeedbackType type);

    List<Feedback> findByStatus(Feedback.FeedbackStatus status);

    List<Feedback> findByCitizenIdAndStatus(UUID citizenId, Feedback.FeedbackStatus status);

    @Query("SELECT f FROM Feedback f WHERE f.citizen.id = :citizenId ORDER BY f.createdAt DESC")
    List<Feedback> findByCitizenIdOrderByCreatedAtDesc(@Param("citizenId") UUID citizenId);

    @Query("SELECT f FROM Feedback f WHERE f.type = :type AND f.status = :status")
    List<Feedback> findByTypeAndStatus(@Param("type") Feedback.FeedbackType type,
                                       @Param("status") Feedback.FeedbackStatus status);

    @Query("SELECT f FROM Feedback f WHERE f.category = :category AND f.status = :status")
    List<Feedback> findByCategoryAndStatus(@Param("category") String category,
                                           @Param("status") Feedback.FeedbackStatus status);

    @Query("SELECT AVG(f.rating) FROM Feedback f WHERE f.rating IS NOT NULL")
    Double findAverageRating();

    @Query("SELECT AVG(f.rating) FROM Feedback f WHERE f.application.id = :applicationId AND f.rating IS NOT NULL")
    Double findAverageRatingByApplicationId(@Param("applicationId") UUID applicationId);

    @Query("SELECT COUNT(f) FROM Feedback f WHERE f.citizen.id = :citizenId AND f.status = :status")
    Long countByCitizenIdAndStatus(@Param("citizenId") UUID citizenId, @Param("status") Feedback.FeedbackStatus status);
}

