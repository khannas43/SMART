package com.smart.citizen.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDate;
import java.util.Map;

@Entity
@Table(name = "schemes", indexes = {
    @Index(name = "idx_schemes_code", columnList = "code"),
    @Index(name = "idx_schemes_category", columnList = "category"),
    @Index(name = "idx_schemes_status", columnList = "status")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Scheme extends BaseEntity {

    @Column(name = "code", unique = true, nullable = false, length = 50)
    private String code;

    @Column(name = "name", nullable = false, length = 255)
    private String name;

    @Column(name = "name_hindi", length = 255)
    private String nameHindi;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "description_hindi", columnDefinition = "TEXT")
    private String descriptionHindi;

    @Column(name = "category", length = 100)
    private String category;

    @Column(name = "department", length = 255)
    private String department;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "eligibility_criteria", columnDefinition = "jsonb")
    private Map<String, Object> eligibilityCriteria;

    @Column(name = "start_date")
    private LocalDate startDate;

    @Column(name = "end_date")
    private LocalDate endDate;

    @Column(name = "status", length = 20)
    @Enumerated(EnumType.STRING)
    private SchemeStatus status = SchemeStatus.ACTIVE;

    public enum SchemeStatus {
        ACTIVE, INACTIVE, CLOSED
    }
}

