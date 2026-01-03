package com.smart.citizen.controller;

import com.smart.citizen.service.ProfileGraphService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * REST API for fetching graph data from Neo4j for frontend visualization
 */
@RestController
@RequestMapping("/profiles/graph")
@CrossOrigin(origins = "*")
public class ProfileGraphController {

    @Autowired
    private ProfileGraphService profileGraphService;

    /**
     * Get family network graph for a citizen
     * Returns nodes and edges with relationship types for visualization
     * 
     * @param identifier Either citizen ID (UUID) or Aadhaar number
     * @param depth Depth of relationships to fetch (default: 2)
     * @return Graph data in format suitable for react-force-graph-2d
     */
    @GetMapping("/family-network/{identifier}")
    public ResponseEntity<Map<String, Object>> getFamilyNetwork(
            @PathVariable String identifier,
            @RequestParam(defaultValue = "2") int depth) {
        
        try {
            Map<String, Object> graphData = profileGraphService.getFamilyNetwork(identifier, depth);
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
        Map<String, Object> legend = profileGraphService.getRelationshipTypes();
        return ResponseEntity.ok(legend);
    }
}

