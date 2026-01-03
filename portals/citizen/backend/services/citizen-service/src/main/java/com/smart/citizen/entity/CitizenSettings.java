package com.smart.citizen.entity;

import com.fasterxml.jackson.databind.JsonNode;
import com.smart.citizen.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "citizen_settings", indexes = {
    @Index(name = "idx_citizen_settings_citizen", columnList = "citizen_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CitizenSettings extends BaseEntity {

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "citizen_id", nullable = false, unique = true, foreignKey = @ForeignKey(name = "fk_settings_citizen"))
    private Citizen citizen;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "notification_preferences", columnDefinition = "jsonb")
    private JsonNode notificationPreferences;

    @Column(name = "quiet_hours_enabled")
    private Boolean quietHoursEnabled = false;

    @Column(name = "quiet_hours_start")
    private LocalTime quietHoursStart;

    @Column(name = "quiet_hours_end")
    private LocalTime quietHoursEnd;

    @Column(name = "opted_out_schemes", columnDefinition = "uuid[]")
    private List<UUID> optedOutSchemes = new ArrayList<>();

    @Column(name = "language_preference", length = 10)
    private String languagePreference = "en";

    @Column(name = "theme_preference", length = 20)
    private String themePreference = "light";

    @Column(name = "two_factor_enabled")
    private Boolean twoFactorEnabled = false;

    @Column(name = "session_timeout_minutes")
    private Integer sessionTimeoutMinutes = 30;
}

