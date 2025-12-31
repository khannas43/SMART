package com.smart.platform.aiml.profile360.controller;

import com.smart.platform.aiml.profile360.service.ProfileGraphService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * REST API for fetching graph data from Neo4j for frontend visualization
 */
@RestController
@RequestMapping("/api/v1/profiles/graph")
@CrossOrigin(origins = "*")
public class ProfileGraphController {

    @Autowired
    private ProfileGraphService profileGraphService;

    /**
     * Get family network graph for a citizen
     * Returns nodes and edges with relationship types for visualization
     * 
     * @param grId Golden Record ID
     * @param depth Depth of relationships to fetch (default: 2)
     * @return Graph data in format suitable for react-force-graph or vis-network
     */
    @GetMapping("/family-network/{grId}")
    public ResponseEntity<Map<String, Object>> getFamilyNetwork(
            @PathVariable UUID grId,
            @RequestParam(defaultValue = "2") int depth) {
        
        try {
            Map<String, Object> graphData = profileGraphService.getFamilyNetwork(grId, depth);
            return ResponseEntity.ok(graphData);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get relationship network for a citizen with all relationship types
     * 
     * @param grId Golden Record ID
     * @param relationshipTypes Optional filter by relationship types (SPOUSE, CHILD, etc.)
     * @return Graph data with nodes and edges
     */
    @GetMapping("/network/{grId}")
    public ResponseEntity<Map<String, Object>> getNetwork(
            @PathVariable UUID grId,
            @RequestParam(required = false) List<String> relationshipTypes) {
        
        try {
            Map<String, Object> graphData = profileGraphService.getNetwork(grId, relationshipTypes);
            return ResponseEntity.ok(graphData);
        } catch (Exception e) {
            return ResponseEntity.internalServerError()
                .body(Map.of("error", e.getMessage()));
        }
    }

    /**
     * Get relationship types legend/mapping for frontend display
     * 
     * @return Map of relationship types with labels, icons, and colors
     */
    @GetMapping("/relationship-types")
    public ResponseEntity<Map<String, Object>> getRelationshipTypes() {
        Map<String, Object> legend = Map.of(
            "SPOUSE", Map.of(
                "label", "Spouse",
                "icon", "👫",
                "color", "#FF6B6B",
                "description", "Married partner"
            ),
            "CHILD", Map.of(
                "label", "Child",
                "icon", "👨‍👩‍👧‍👦",
                "color", "#4ECDC4",
                "description", "Parent → Child relationship"
            ),
            "PARENT", Map.of(
                "label", "Parent",
                "icon", "👨‍👩‍👧‍👦",
                "color", "#95E1D3",
                "description", "Child → Parent relationship"
            ),
            "SIBLING", Map.of(
                "label", "Sibling",
                "icon", "👨‍👩‍👧‍👦",
                "color", "#F38181",
                "description", "Brother or Sister"
            ),
            "CO_RESIDENT", Map.of(
                "label", "Co-Resident",
                "icon", "🏠",
                "color", "#AA96DA",
                "description", "Living at same address"
            ),
            "CO_BENEFIT", Map.of(
                "label", "Co-Benefit",
                "icon", "💰",
                "color", "#FECA57",
                "description", "Receiving same benefits"
            ),
            "EMPLOYEE_OF", Map.of(
                "label", "Employee",
                "icon", "💼",
                "color", "#48DBFB",
                "description", "Employee → Employer"
            ),
            "BUSINESS_PARTNER", Map.of(
                "label", "Business Partner",
                "icon", "🤝",
                "color", "#10AC84",
                "description", "Business partnership"
            ),
            "SHG_MEMBER", Map.of(
                "label", "SHG Member",
                "icon", "👥",
                "color", "#5F27CD",
                "description", "Self-Help Group member"
            )
        );
        
        return ResponseEntity.ok(legend);
    }
}

