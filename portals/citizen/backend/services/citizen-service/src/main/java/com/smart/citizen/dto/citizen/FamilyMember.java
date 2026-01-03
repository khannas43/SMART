package com.smart.citizen.dto.citizen;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FamilyMember {
    private UUID id;
    private String name;
    private String nameHindi;
    private String relationship;
    private Integer age;
    private String gender;
    private Integer confidence;
    private String aadhaarNumber;
    private String mobileNumber;
    private LocalDate dateOfBirth;
    private String incomeBand;
    private String vulnerabilityCategory;
}

