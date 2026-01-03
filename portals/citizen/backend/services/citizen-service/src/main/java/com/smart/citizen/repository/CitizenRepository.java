package com.smart.citizen.repository;

import com.smart.citizen.entity.Citizen;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface CitizenRepository extends JpaRepository<Citizen, UUID> {

    Optional<Citizen> findByMobileNumber(String mobileNumber);

    Optional<Citizen> findByAadhaarNumber(String aadhaarNumber);

    Optional<Citizen> findByEmail(String email);

    List<Citizen> findByStatus(Citizen.CitizenStatus status);

    List<Citizen> findByVerificationStatus(Citizen.VerificationStatus verificationStatus);

    @Query("SELECT c FROM Citizen c WHERE c.mobileNumber = :mobileNumber OR c.aadhaarNumber = :aadhaarNumber")
    Optional<Citizen> findByMobileNumberOrAadhaarNumber(@Param("mobileNumber") String mobileNumber, 
                                                         @Param("aadhaarNumber") String aadhaarNumber);

    boolean existsByMobileNumber(String mobileNumber);

    boolean existsByAadhaarNumber(String aadhaarNumber);

    boolean existsByEmail(String email);

    @Query("SELECT c FROM Citizen c WHERE c.district = :district AND c.status = 'ACTIVE'")
    List<Citizen> findByDistrict(@Param("district") String district);

    @Query("SELECT c FROM Citizen c WHERE c.city = :city AND c.status = 'ACTIVE'")
    List<Citizen> findByCity(@Param("city") String city);

    @Query("SELECT c FROM Citizen c WHERE c.addressLine1 = :addressLine1 AND c.status = 'ACTIVE'")
    List<Citizen> findByAddressLine1(@Param("addressLine1") String addressLine1);
}

