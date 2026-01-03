package com.smart.citizen.repository;

import com.smart.citizen.entity.Document;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DocumentRepository extends JpaRepository<Document, UUID> {

    List<Document> findByCitizenId(UUID citizenId);

    List<Document> findByApplicationId(UUID applicationId);

    List<Document> findByCitizenIdAndDocumentType(UUID citizenId, String documentType);

    List<Document> findByApplicationIdAndDocumentType(UUID applicationId, String documentType);

    List<Document> findByVerificationStatus(Document.VerificationStatus verificationStatus);

    @Query("SELECT d FROM Document d WHERE d.citizen.id = :citizenId AND d.verificationStatus = :status")
    List<Document> findByCitizenIdAndVerificationStatus(@Param("citizenId") UUID citizenId,
                                                         @Param("status") Document.VerificationStatus status);

    @Query("SELECT d FROM Document d WHERE d.application.id = :applicationId AND d.verificationStatus = :status")
    List<Document> findByApplicationIdAndVerificationStatus(@Param("applicationId") UUID applicationId,
                                                            @Param("status") Document.VerificationStatus status);

    @Query("SELECT d FROM Document d WHERE d.documentType = :documentType AND d.citizen.id = :citizenId ORDER BY d.uploadedAt DESC")
    List<Document> findByDocumentTypeAndCitizenIdOrderByUploadedAtDesc(@Param("documentType") String documentType,
                                                                        @Param("citizenId") UUID citizenId);

    @Query("SELECT COUNT(d) FROM Document d WHERE d.application.id = :applicationId")
    Long countByApplicationId(@Param("applicationId") UUID applicationId);

    @Query("SELECT COUNT(d) FROM Document d WHERE d.citizen.id = :citizenId AND d.verificationStatus = 'PENDING'")
    Long countPendingDocumentsByCitizenId(@Param("citizenId") UUID citizenId);

    // Search methods
    @Query("SELECT d FROM Document d WHERE d.citizen.id = :citizenId AND " +
           "(LOWER(d.documentName) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(d.documentType) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<Document> searchByCitizenId(@Param("citizenId") UUID citizenId, @Param("query") String query);
}

