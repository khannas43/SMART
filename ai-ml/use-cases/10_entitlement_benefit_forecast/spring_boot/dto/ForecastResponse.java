package com.smart.platform.forecast.dto;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * Forecast Response DTO
 * Use Case ID: AI-PLATFORM-10
 */
public class ForecastResponse {
    private Boolean success;
    private Integer forecastId;
    private String familyId;
    private String forecastType; // BASELINE, SCENARIO
    private String scenarioName;
    private String scenarioDescription;
    private Integer horizonMonths;
    private String startDate;
    private Integer schemeCount;
    private List<ProjectionResponse> projections;
    private BigDecimal totalAnnualValue;
    private BigDecimal totalForecastValue;
    private String uncertaintyLevel; // LOW, MEDIUM, HIGH
    private List<String> assumptions;
    private LocalDateTime generatedAt;
    private String message;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() { return success; }
    public void setSuccess(Boolean success) { this.success = success; }
    public Integer getForecastId() { return forecastId; }
    public void setForecastId(Integer forecastId) { this.forecastId = forecastId; }
    public String getFamilyId() { return familyId; }
    public void setFamilyId(String familyId) { this.familyId = familyId; }
    public String getForecastType() { return forecastType; }
    public void setForecastType(String forecastType) { this.forecastType = forecastType; }
    public String getScenarioName() { return scenarioName; }
    public void setScenarioName(String scenarioName) { this.scenarioName = scenarioName; }
    public String getScenarioDescription() { return scenarioDescription; }
    public void setScenarioDescription(String scenarioDescription) { this.scenarioDescription = scenarioDescription; }
    public Integer getHorizonMonths() { return horizonMonths; }
    public void setHorizonMonths(Integer horizonMonths) { this.horizonMonths = horizonMonths; }
    public String getStartDate() { return startDate; }
    public void setStartDate(String startDate) { this.startDate = startDate; }
    public Integer getSchemeCount() { return schemeCount; }
    public void setSchemeCount(Integer schemeCount) { this.schemeCount = schemeCount; }
    public List<ProjectionResponse> getProjections() { return projections; }
    public void setProjections(List<ProjectionResponse> projections) { this.projections = projections; }
    public BigDecimal getTotalAnnualValue() { return totalAnnualValue; }
    public void setTotalAnnualValue(BigDecimal totalAnnualValue) { this.totalAnnualValue = totalAnnualValue; }
    public BigDecimal getTotalForecastValue() { return totalForecastValue; }
    public void setTotalForecastValue(BigDecimal totalForecastValue) { this.totalForecastValue = totalForecastValue; }
    public String getUncertaintyLevel() { return uncertaintyLevel; }
    public void setUncertaintyLevel(String uncertaintyLevel) { this.uncertaintyLevel = uncertaintyLevel; }
    public List<String> getAssumptions() { return assumptions; }
    public void setAssumptions(List<String> assumptions) { this.assumptions = assumptions; }
    public LocalDateTime getGeneratedAt() { return generatedAt; }
    public void setGeneratedAt(LocalDateTime generatedAt) { this.generatedAt = generatedAt; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    public String getError() { return error; }
    public void setError(String error) { this.error = error; }

    /**
     * Projection Response (nested DTO)
     */
    public static class ProjectionResponse {
        private Integer projectionId;
        private String schemeCode;
        private String schemeName;
        private String projectionType; // CURRENT_ENROLMENT, FUTURE_ENROLMENT, POLICY_CHANGE
        private String periodStart;
        private String periodEnd;
        private String periodType; // MONTHLY, QUARTERLY, ANNUAL, SEASONAL
        private BigDecimal benefitAmount;
        private String benefitFrequency;
        private BigDecimal probability;
        private String confidenceLevel;
        private List<String> assumptions;
        private String lifeStageEvent;
        private String eventDate;

        // Getters and Setters
        public Integer getProjectionId() { return projectionId; }
        public void setProjectionId(Integer projectionId) { this.projectionId = projectionId; }
        public String getSchemeCode() { return schemeCode; }
        public void setSchemeCode(String schemeCode) { this.schemeCode = schemeCode; }
        public String getSchemeName() { return schemeName; }
        public void setSchemeName(String schemeName) { this.schemeName = schemeName; }
        public String getProjectionType() { return projectionType; }
        public void setProjectionType(String projectionType) { this.projectionType = projectionType; }
        public String getPeriodStart() { return periodStart; }
        public void setPeriodStart(String periodStart) { this.periodStart = periodStart; }
        public String getPeriodEnd() { return periodEnd; }
        public void setPeriodEnd(String periodEnd) { this.periodEnd = periodEnd; }
        public String getPeriodType() { return periodType; }
        public void setPeriodType(String periodType) { this.periodType = periodType; }
        public BigDecimal getBenefitAmount() { return benefitAmount; }
        public void setBenefitAmount(BigDecimal benefitAmount) { this.benefitAmount = benefitAmount; }
        public String getBenefitFrequency() { return benefitFrequency; }
        public void setBenefitFrequency(String benefitFrequency) { this.benefitFrequency = benefitFrequency; }
        public BigDecimal getProbability() { return probability; }
        public void setProbability(BigDecimal probability) { this.probability = probability; }
        public String getConfidenceLevel() { return confidenceLevel; }
        public void setConfidenceLevel(String confidenceLevel) { this.confidenceLevel = confidenceLevel; }
        public List<String> getAssumptions() { return assumptions; }
        public void setAssumptions(List<String> assumptions) { this.assumptions = assumptions; }
        public String getLifeStageEvent() { return lifeStageEvent; }
        public void setLifeStageEvent(String lifeStageEvent) { this.lifeStageEvent = lifeStageEvent; }
        public String getEventDate() { return eventDate; }
        public void setEventDate(String eventDate) { this.eventDate = eventDate; }
    }
}

