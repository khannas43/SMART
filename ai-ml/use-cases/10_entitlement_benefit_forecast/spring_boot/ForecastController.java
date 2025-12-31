package com.smart.platform.forecast.controller;

import com.smart.platform.forecast.dto.ForecastResponse;
import com.smart.platform.forecast.service.ForecastService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST Controller for Entitlement & Benefit Forecast (AI-PLATFORM-10)
 */
@RestController
@RequestMapping("/forecast")
@CrossOrigin(origins = "*")
public class ForecastController {

    @Autowired
    private ForecastService forecastService;

    /**
     * Generate benefit forecast for a household
     * GET /forecast/benefits?family_id={id}&horizon=12m&scenario={name}
     */
    @GetMapping("/benefits")
    public ResponseEntity<ForecastResponse> getForecast(
            @RequestParam String familyId,
            @RequestParam(required = false, defaultValue = "12") Integer horizon,
            @RequestParam(required = false) String scenario) {
        try {
            ForecastResponse response = forecastService.generateForecast(familyId, horizon, scenario);
            if (response.getSuccess()) {
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
            }
        } catch (Exception e) {
            ForecastResponse errorResponse = new ForecastResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get existing forecast
     * GET /forecast/{forecastId}
     */
    @GetMapping("/{forecastId}")
    public ResponseEntity<ForecastResponse> getForecastById(@PathVariable Integer forecastId) {
        try {
            ForecastResponse response = forecastService.getForecastById(forecastId);
            if (response.getSuccess()) {
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
            }
        } catch (Exception e) {
            ForecastResponse errorResponse = new ForecastResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get latest forecast for family
     * GET /forecast/family/{familyId}/latest
     */
    @GetMapping("/family/{familyId}/latest")
    public ResponseEntity<ForecastResponse> getLatestForecast(@PathVariable String familyId) {
        try {
            ForecastResponse response = forecastService.getLatestForecast(familyId);
            if (response.getSuccess()) {
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body(response);
            }
        } catch (Exception e) {
            ForecastResponse errorResponse = new ForecastResponse();
            errorResponse.setSuccess(false);
            errorResponse.setError(e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }

    /**
     * Get aggregate forecast (for planning)
     * GET /forecast/aggregate?level={block|district|state}&block_id={id}&model={arima|prophet}
     */
    @GetMapping("/aggregate")
    public ResponseEntity<Map<String, Object>> getAggregateForecast(
            @RequestParam String level,
            @RequestParam(required = false) String blockId,
            @RequestParam(required = false) String district,
            @RequestParam(required = false) String state,
            @RequestParam(required = false, defaultValue = "12") Integer horizon,
            @RequestParam(required = false) String scenario,
            @RequestParam(required = false, defaultValue = "ARIMA") String modelType,
            @RequestParam(required = false) List<String> schemeCodes) {
        try {
            Map<String, Object> response = forecastService.getAggregateForecast(
                    level, blockId, district, state, horizon, scenario, modelType, schemeCodes);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("success", false, "error", e.getMessage()));
        }
    }

    /**
     * Estimate recommendation probability
     * GET /forecast/probability?family_id={id}&scheme_code={code}&eligibility_status={status}&rank={rank}
     */
    @GetMapping("/probability")
    public ResponseEntity<Map<String, Object>> estimateProbability(
            @RequestParam String familyId,
            @RequestParam String schemeCode,
            @RequestParam String eligibilityStatus,
            @RequestParam Integer rank,
            @RequestParam(required = false, defaultValue = "0") Integer daysSince) {
        try {
            Map<String, Object> response = forecastService.estimateProbability(
                    familyId, schemeCode, eligibilityStatus, rank, daysSince);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("success", false, "error", e.getMessage()));
        }
    }

    /**
     * Handle event and refresh forecast
     * POST /forecast/refresh-event
     */
    @PostMapping("/refresh-event")
    public ResponseEntity<Map<String, Object>> handleEvent(
            @RequestParam String eventType,
            @RequestBody Map<String, Object> eventData) {
        try {
            Map<String, Object> response = forecastService.handleEvent(eventType, eventData);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("success", false, "error", e.getMessage()));
        }
    }

    /**
     * Refresh stale forecasts
     * POST /forecast/refresh-stale?days_stale={days}&limit={limit}
     */
    @PostMapping("/refresh-stale")
    public ResponseEntity<Map<String, Object>> refreshStaleForecasts(
            @RequestParam(required = false, defaultValue = "30") Integer daysStale,
            @RequestParam(required = false, defaultValue = "100") Integer limit) {
        try {
            Map<String, Object> response = forecastService.refreshStaleForecasts(daysStale, limit);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("success", false, "error", e.getMessage()));
        }
    }
}

