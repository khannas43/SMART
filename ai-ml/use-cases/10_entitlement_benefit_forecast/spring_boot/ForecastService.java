package com.smart.platform.forecast.service;

import com.smart.platform.forecast.dto.ForecastResponse;
import com.smart.platform.forecast.service.PythonForecastClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * Forecast Service
 * Use Case ID: AI-PLATFORM-10
 */
@Service
public class ForecastService {

    @Autowired
    private PythonForecastClient pythonForecastClient;

    /**
     * Generate forecast
     */
    public ForecastResponse generateForecast(String familyId, Integer horizon, String scenario) {
        Map<String, Object> result = pythonForecastClient.generateForecast(
                familyId, horizon != null ? horizon : 12, scenario);
        
        return mapToForecastResponse(result);
    }

    /**
     * Get forecast by ID
     */
    public ForecastResponse getForecastById(Integer forecastId) {
        Map<String, Object> result = pythonForecastClient.getForecastById(forecastId);
        return mapToForecastResponse(result);
    }

    /**
     * Get latest forecast for family
     */
    public ForecastResponse getLatestForecast(String familyId) {
        Map<String, Object> result = pythonForecastClient.getLatestForecast(familyId);
        return mapToForecastResponse(result);
    }

    /**
     * Get aggregate forecast
     */
    public Map<String, Object> getAggregateForecast(
            String level, String blockId, String district, String state, 
            Integer horizon, String scenario, String modelType, List<String> schemeCodes) {
        return pythonForecastClient.getAggregateForecast(
                level, blockId, district, state, horizon, scenario, modelType, schemeCodes);
    }

    /**
     * Estimate recommendation probability
     */
    public Map<String, Object> estimateProbability(
            String familyId, String schemeCode, String eligibilityStatus, 
            Integer rank, Integer daysSince) {
        return pythonForecastClient.estimateProbability(
                familyId, schemeCode, eligibilityStatus, rank, daysSince);
    }

    /**
     * Handle event and refresh forecast
     */
    public Map<String, Object> handleEvent(String eventType, Map<String, Object> eventData) {
        return pythonForecastClient.handleEvent(eventType, eventData);
    }

    /**
     * Refresh stale forecasts
     */
    public Map<String, Object> refreshStaleForecasts(Integer daysStale, Integer limit) {
        return pythonForecastClient.refreshStaleForecasts(daysStale, limit);
    }

    /**
     * Map Python result to ForecastResponse
     */
    private ForecastResponse mapToForecastResponse(Map<String, Object> result) {
        ForecastResponse response = new ForecastResponse();
        
        response.setSuccess((Boolean) result.getOrDefault("success", true));
        response.setForecastId((Integer) result.get("forecast_id"));
        response.setFamilyId((String) result.get("family_id"));
        response.setForecastType((String) result.get("forecast_type"));
        response.setScenarioName((String) result.get("scenario_name"));
        response.setScenarioDescription((String) result.get("scenario_description"));
        response.setHorizonMonths((Integer) result.get("horizon_months"));
        response.setStartDate((String) result.get("start_date"));
        response.setSchemeCount((Integer) result.get("scheme_count"));
        response.setTotalAnnualValue(convertToBigDecimal(result.get("total_annual_value")));
        response.setTotalForecastValue(convertToBigDecimal(result.get("total_forecast_value")));
        response.setUncertaintyLevel((String) result.get("uncertainty_level"));
        response.setAssumptions((java.util.List<String>) result.get("assumptions"));
        response.setMessage((String) result.get("message"));
        response.setError((String) result.get("error"));
        
        // Map projections
        if (result.containsKey("projections")) {
            // Implementation would map projections list
        }
        
        return response;
    }

    private java.math.BigDecimal convertToBigDecimal(Object value) {
        if (value == null) return java.math.BigDecimal.ZERO;
        if (value instanceof Number) {
            return java.math.BigDecimal.valueOf(((Number) value).doubleValue());
        }
        return new java.math.BigDecimal(value.toString());
    }
}

