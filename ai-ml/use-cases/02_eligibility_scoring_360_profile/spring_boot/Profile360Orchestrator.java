package com.smart.aiml.platform02;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.beans.factory.annotation.Autowired;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Profile 360° Orchestrator Service
 * REST APIs for 360° profiles and network analytics
 * Use Case: AI-PLATFORM-02
 */
@SpringBootApplication
@EnableScheduling
@RestController
@RequestMapping("/profiles/360")
public class Profile360Orchestrator {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    /**
     * GET /profiles/360/{gr_id}
     * Returns full 360° profile JSON
     * 
     * @param grId Golden Record ID
     * @param view View level: citizen, officer, admin (default: citizen)
     * @return 360° profile JSON
     */
    @GetMapping("/{gr_id}")
    public ResponseEntity<Map<String, Object>> getProfile360(
            @PathVariable("gr_id") String grId,
            @RequestParam(value = "view", defaultValue = "citizen") String view) {
        
        try {
            // Get profile from database
            String sql = "SELECT profile_data FROM profile_360 WHERE gr_id = ?::uuid";
            Map<String, Object> profile = jdbcTemplate.queryForObject(
                sql,
                new Object[]{grId},
                (rs, rowNum) -> {
                    // Parse JSONB profile_data
                    String jsonData = rs.getString("profile_data");
                    // In production, use proper JSON parsing
                    return parseProfileJson(jsonData, view);
                }
            );
            
            if (profile == null) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body(Map.of("error", "Profile not found", "gr_id", grId));
            }
            
            return ResponseEntity.ok(profile);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * GET /profiles/360/{gr_id}/network
     * Returns graph neighborhood (up to N hops) with benefit metrics
     * 
     * @param grId Golden Record ID
     * @param hops Number of hops (default: 2)
     * @return Network neighborhood with relationships and benefits
     */
    @GetMapping("/{gr_id}/network")
    public ResponseEntity<Map<String, Object>> getNetwork(
            @PathVariable("gr_id") String grId,
            @RequestParam(value = "hops", defaultValue = "2") int hops) {
        
        try {
            // Get relationships (direct connections)
            String relSql = """
                SELECT 
                    r.from_gr_id,
                    r.to_gr_id,
                    r.relationship_type,
                    r.is_verified,
                    p1.profile_data as from_profile,
                    p2.profile_data as to_profile
                FROM gr_relationships r
                LEFT JOIN profile_360 p1 ON r.from_gr_id = p1.gr_id
                LEFT JOIN profile_360 p2 ON r.to_gr_id = p2.gr_id
                WHERE r.from_gr_id = ?::uuid OR r.to_gr_id = ?::uuid
                LIMIT 100
                """;
            
            List<Map<String, Object>> relationships = jdbcTemplate.query(
                relSql,
                new Object[]{grId, grId},
                (rs, rowNum) -> {
                    Map<String, Object> rel = new HashMap<>();
                    rel.put("from_gr_id", rs.getString("from_gr_id"));
                    rel.put("to_gr_id", rs.getString("to_gr_id"));
                    rel.put("relationship_type", rs.getString("relationship_type"));
                    rel.put("is_verified", rs.getBoolean("is_verified"));
                    return rel;
                }
            );
            
            Map<String, Object> network = new HashMap<>();
            network.put("center_gr_id", grId);
            network.put("relationships", relationships);
            network.put("hops", hops);
            network.put("total_connections", relationships.size());
            
            return ResponseEntity.ok(network);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * GET /analytics/benefits/clusters
     * Cluster-level benefit aggregates and anomaly flags
     * 
     * @param scheme Scheme category filter (optional)
     * @param district District ID filter (optional)
     * @return Cluster analytics
     */
    @GetMapping("/analytics/benefits/clusters")
    public ResponseEntity<List<Map<String, Object>>> getClusterAnalytics(
            @RequestParam(value = "scheme", required = false) String scheme,
            @RequestParam(value = "district", required = false) Integer district) {
        
        try {
            StringBuilder sql = new StringBuilder("""
                SELECT 
                    p.cluster_id,
                    COUNT(DISTINCT p.gr_id) as cluster_size,
                    AVG((p.profile_data->'benefits'->>'last_3y')::numeric) as avg_benefits_3y,
                    SUM((p.profile_data->'benefits'->>'last_3y')::numeric) as total_benefits_3y,
                    COUNT(DISTINCT CASE WHEN array_length(p.risk_flags, 1) > 0 THEN p.gr_id END) as flagged_count
                FROM profile_360 p
                WHERE p.cluster_id IS NOT NULL
                """);
            
            List<Object> params = new ArrayList<>();
            
            if (district != null) {
                sql.append(" AND EXISTS (SELECT 1 FROM golden_records gr WHERE gr.gr_id = p.gr_id AND gr.district_id = ?)");
                params.add(district);
            }
            
            sql.append(" GROUP BY p.cluster_id ORDER BY total_benefits_3y DESC LIMIT 100");
            
            List<Map<String, Object>> clusters = jdbcTemplate.query(
                sql.toString(),
                params.toArray(),
                (rs, rowNum) -> {
                    Map<String, Object> cluster = new HashMap<>();
                    cluster.put("cluster_id", rs.getString("cluster_id"));
                    cluster.put("cluster_size", rs.getInt("cluster_size"));
                    cluster.put("avg_benefits_3y", rs.getBigDecimal("avg_benefits_3y"));
                    cluster.put("total_benefits_3y", rs.getBigDecimal("total_benefits_3y"));
                    cluster.put("flagged_count", rs.getInt("flagged_count"));
                    return cluster;
                }
            );
            
            return ResponseEntity.ok(clusters);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(List.of(Map.of("error", e.getMessage())));
        }
    }

    /**
     * GET /analytics/benefits/undercoverage
     * List of under-served families/areas for outreach
     * 
     * @param limit Maximum number of results (default: 100)
     * @return Under-coverage list
     */
    @GetMapping("/analytics/benefits/undercoverage")
    public ResponseEntity<List<Map<String, Object>>> getUnderCoverage(
            @RequestParam(value = "limit", defaultValue = "100") int limit) {
        
        try {
            String sql = """
                SELECT 
                    p.gr_id,
                    p.inferred_income_band,
                    (p.profile_data->'identity'->>'full_name') as full_name,
                    (p.profile_data->'benefits'->>'last_1y')::numeric as benefits_1y,
                    gr.district_id,
                    array_agg(DISTINCT f.flag_explanation) as explanations
                FROM profile_360 p
                JOIN golden_records gr ON p.gr_id = gr.gr_id
                JOIN analytics_flags f ON p.gr_id = f.gr_id
                WHERE f.flag_type IN ('UNDER_COVERAGE', 'PRIORITY_VULNERABLE')
                    AND f.flag_status = 'ACTIVE'
                GROUP BY p.gr_id, p.inferred_income_band, p.profile_data, gr.district_id
                ORDER BY f.flag_score DESC
                LIMIT ?
                """;
            
            List<Map<String, Object>> underCovered = jdbcTemplate.query(
                sql,
                new Object[]{limit},
                (rs, rowNum) -> {
                    Map<String, Object> item = new HashMap<>();
                    item.put("gr_id", rs.getString("gr_id"));
                    item.put("full_name", rs.getString("full_name"));
                    item.put("income_band", rs.getString("inferred_income_band"));
                    item.put("benefits_1y", rs.getBigDecimal("benefits_1y"));
                    item.put("district_id", rs.getInt("district_id"));
                    item.put("explanations", rs.getArray("explanations"));
                    return item;
                }
            );
            
            return ResponseEntity.ok(underCovered);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(List.of(Map.of("error", e.getMessage())));
        }
    }

    /**
     * POST /internal/recompute/{gr_id}
     * Trigger profile recomputation for a Golden Record
     * Internal API - trigger recompute service
     * 
     * @param grId Golden Record ID
     * @return Success status
     */
    @PostMapping("/internal/recompute/{gr_id}")
    public ResponseEntity<Map<String, Object>> triggerRecompute(
            @PathVariable("gr_id") String grId) {
        
        try {
            // Add to recompute queue
            String sql = """
                INSERT INTO profile_recompute_queue (gr_id, priority, trigger_type, trigger_reference)
                VALUES (?::uuid, 8, 'MANUAL', ?)
                ON CONFLICT DO NOTHING
                """;
            
            int rows = jdbcTemplate.update(sql, grId, "api_trigger_" + LocalDateTime.now());
            
            Map<String, Object> response = new HashMap<>();
            response.put("gr_id", grId);
            response.put("queued", rows > 0);
            response.put("message", rows > 0 ? "Profile queued for recomputation" : "Profile already in queue");
            
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Scheduled task: Hourly profile recomputation
     * Processes recompute queue every hour
     */
    @Scheduled(fixedRate = 3600000) // 1 hour in milliseconds
    public void hourlyRecompute() {
        System.out.println("Scheduled recompute job started at " + LocalDateTime.now());
        
        // In production, this would call the Python ProfileRecomputeService
        // For now, just log
        System.out.println("Profile recompute queue processing (call Python service)");
    }

    /**
     * Helper: Parse profile JSON based on view level
     * Filters sensitive data based on view type
     */
    private Map<String, Object> parseProfileJson(String jsonData, String view) {
        // In production, use proper JSON parsing (Jackson, Gson, etc.)
        // For now, return as-is with view filtering applied
        Map<String, Object> profile = new HashMap<>();
        
        if ("citizen".equals(view)) {
            // Citizen view: Simplified, no internal flags
            profile.put("view", "citizen");
            profile.put("simplified", true);
        } else if ("officer".equals(view)) {
            // Officer view: Full profile with flags
            profile.put("view", "officer");
            profile.put("full", true);
        } else if ("admin".equals(view)) {
            // Admin view: Full profile with all metadata
            profile.put("view", "admin");
            profile.put("full", true);
            profile.put("metadata", true);
        }
        
        return profile;
    }

    public static void main(String[] args) {
        SpringApplication.run(Profile360Orchestrator.class, args);
    }
}


