package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "citizens", indexes = {
    @Index(name = "idx_citizens_mobile", columnList = "mobile_number"),
    @Index(name = "idx_citizens_aadhaar", columnList = "aadhaar_number"),
    @Index(name = "idx_citizens_status", columnList = "status")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Citizen extends BaseEntity {

    @Column(name = "aadhaar_number", unique = true, length = 12)
    private String aadhaarNumber;

    @Column(name = "mobile_number", nullable = false, length = 10)
    private String mobileNumber;

    @Column(name = "email", length = 255)
    private String email;

    @Column(name = "full_name", nullable = false, length = 255)
    private String fullName;

    @Column(name = "full_name_hindi", length = 255)
    private String fullNameHindi;

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;

    @Column(name = "gender", length = 10)
    private String gender;

    @Column(name = "address_line1", columnDefinition = "TEXT")
    private String addressLine1;

    @Column(name = "address_line2", columnDefinition = "TEXT")
    private String addressLine2;

    @Column(name = "city", length = 100)
    private String city;

    @Column(name = "district", length = 100)
    private String district;

    @Column(name = "state", length = 100)
    private String state = "Rajasthan";

    @Column(name = "pincode", length = 6)
    private String pincode;

    @Column(name = "status", length = 20)
    @Enumerated(EnumType.STRING)
    private CitizenStatus status = CitizenStatus.ACTIVE;

    @Column(name = "verification_status", length = 20)
    @Enumerated(EnumType.STRING)
    private VerificationStatus verificationStatus = VerificationStatus.PENDING;

    @Column(name = "last_login_at")
    private LocalDateTime lastLoginAt;

    @Column(name = "created_by")
    private UUID createdBy;

    @Column(name = "updated_by")
    private UUID updatedBy;

    public enum CitizenStatus {
        ACTIVE, INACTIVE, SUSPENDED, VERIFIED
    }

    public enum VerificationStatus {
        PENDING, VERIFIED, REJECTED
    }
}

