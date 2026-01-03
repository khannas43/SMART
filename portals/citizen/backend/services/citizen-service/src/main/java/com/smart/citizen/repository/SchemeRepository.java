package com.smart.citizen.repository;

import com.smart.citizen.entity.Scheme;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SchemeRepository extends JpaRepository<Scheme, UUID> {

    Optional<Scheme> findByCode(String code);

    List<Scheme> findByStatus(Scheme.SchemeStatus status);

    List<Scheme> findByCategory(String category);

    @Query("SELECT s FROM Scheme s WHERE s.status = :status AND " +
           "(:startDate IS NULL OR s.startDate IS NULL OR s.startDate <= :startDate) AND " +
           "(:endDate IS NULL OR s.endDate IS NULL OR s.endDate >= :endDate)")
    List<Scheme> findActiveSchemes(@Param("status") Scheme.SchemeStatus status,
                                   @Param("startDate") LocalDate startDate,
                                   @Param("endDate") LocalDate endDate);

    @Query("SELECT s FROM Scheme s WHERE s.department = :department AND s.status = 'ACTIVE'")
    List<Scheme> findByDepartment(@Param("department") String department);

    @Query("SELECT s FROM Scheme s WHERE s.status = 'ACTIVE' ORDER BY s.name ASC")
    List<Scheme> findAllActiveSchemes();

    boolean existsByCode(String code);

    // Search methods
    @Query("SELECT s FROM Scheme s WHERE " +
           "(LOWER(s.name) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.description) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.code) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.category) LIKE LOWER(CONCAT('%', :query, '%')) OR " +
           "LOWER(s.department) LIKE LOWER(CONCAT('%', :query, '%'))) " +
           "AND s.status = 'ACTIVE'")
    List<Scheme> searchActiveSchemes(@Param("query") String query);
}

