package com.smart.citizen.repository;

import com.smart.citizen.entity.ServiceApplication;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ServiceApplicationRepository extends JpaRepository<ServiceApplication, UUID> {

    Optional<ServiceApplication> findByApplicationNumber(String applicationNumber);

    List<ServiceApplication> findByCitizenId(UUID citizenId);

    // Query to get paginated IDs only (for pagination count)
    @Query("SELECT a.id FROM ServiceApplication a WHERE a.citizen.id = :citizenId")
    Page<UUID> findIdsByCitizenId(@Param("citizenId") UUID citizenId, Pageable pageable);
    
    // Query to fetch applications with relationships for given IDs
    @Query("SELECT DISTINCT a FROM ServiceApplication a LEFT JOIN FETCH a.citizen LEFT JOIN FETCH a.scheme WHERE a.id IN :ids")
    List<ServiceApplication> findByIdInWithCitizenAndScheme(@Param("ids") List<UUID> ids);

    List<ServiceApplication> findByCitizenIdAndStatus(UUID citizenId, ServiceApplication.ApplicationStatus status);

    List<ServiceApplication> findBySchemeId(UUID schemeId);

    List<ServiceApplication> findByStatus(ServiceApplication.ApplicationStatus status);

    Page<ServiceApplication> findByStatus(ServiceApplication.ApplicationStatus status, Pageable pageable);

    @Query("SELECT a FROM ServiceApplication a WHERE a.citizen.id = :citizenId ORDER BY a.submissionDate DESC")
    List<ServiceApplication> findByCitizenIdOrderBySubmissionDateDesc(@Param("citizenId") UUID citizenId);

    @Query("SELECT a FROM ServiceApplication a WHERE a.citizen.id = :citizenId AND a.serviceType = :serviceType")
    List<ServiceApplication> findByCitizenIdAndServiceType(@Param("citizenId") UUID citizenId, 
                                                            @Param("serviceType") String serviceType);

    @Query("SELECT a FROM ServiceApplication a WHERE a.assignedToDept = :department AND a.status = :status")
    List<ServiceApplication> findByAssignedToDeptAndStatus(@Param("department") String department,
                                                           @Param("status") ServiceApplication.ApplicationStatus status);

    @Query("SELECT a FROM ServiceApplication a WHERE a.assignedToOfficer = :officerId AND a.status = :status")
    List<ServiceApplication> findByAssignedToOfficerAndStatus(@Param("officerId") UUID officerId,
                                                              @Param("status") ServiceApplication.ApplicationStatus status);

    @Query("SELECT a FROM ServiceApplication a WHERE a.submissionDate >= :startDate AND a.submissionDate <= :endDate")
    List<ServiceApplication> findBySubmissionDateBetween(@Param("startDate") LocalDateTime startDate,
                                                          @Param("endDate") LocalDateTime endDate);

    @Query("SELECT COUNT(a) FROM ServiceApplication a WHERE a.citizen.id = :citizenId AND a.status = :status")
    Long countByCitizenIdAndStatus(@Param("citizenId") UUID citizenId, 
                                   @Param("status") ServiceApplication.ApplicationStatus status);

    boolean existsByApplicationNumber(String applicationNumber);

    // Search methods
    @Query("SELECT a FROM ServiceApplication a WHERE a.citizen.id = :citizenId AND " +
           "(LOWER(a.applicationNumber) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(a.serviceType) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(a.subject) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(a.description) LIKE LOWER(CONCAT('%', :query, '%')))")
    List<ServiceApplication> searchByCitizenId(@Param("citizenId") UUID citizenId, @Param("query") String query);
}

