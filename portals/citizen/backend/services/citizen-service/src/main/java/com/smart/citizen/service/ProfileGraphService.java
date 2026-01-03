package com.smart.citizen.service;

import org.neo4j.driver.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service to fetch graph data from Neo4j for family relationship visualization
 */
@Service
public class ProfileGraphService {

    @Value("${neo4j.uri:bolt://172.17.16.1:7687}")
    private String neo4jUri;

    @Value("${neo4j.user:neo4j}")
    private String neo4jUser;

    @Value("${neo4j.password:anjali143}")
    private String neo4jPassword;

    @Value("${neo4j.database:smartgraphdb}")
    private String neo4jDatabase;

    private Driver driver;

    private Driver getDriver() {
        if (driver == null) {
            driver = GraphDatabase.driver(neo4jUri, AuthTokens.basic(neo4jUser, neo4jPassword));
        }
        return driver;
    }

    /**
     * Get family network graph data formatted for frontend visualization
     * Supports querying by gr_id (UUID) or jan_aadhaar (Aadhaar number)
     * 
     * @param identifier Either gr_id (UUID string) or jan_aadhaar (12-digit Aadhaar)
     * @param depth Depth of relationships to fetch
     * @return Map with "nodes" and "links" arrays
     */
    public Map<String, Object> getFamilyNetwork(String identifier, int depth) {
        try (Session session = getDriver().session(SessionConfig.forDatabase(neo4jDatabase))) {
            // Determine if identifier is UUID (gr_id) or Aadhaar (jan_aadhaar)
            boolean isUuid = identifier.matches("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}");
            String matchProperty = isUuid ? "gr_id" : "jan_aadhaar";
            
            String cypher = String.format("""
                MATCH path = (start:GoldenRecord {%s: $identifier})-[r:RELATED_TO*1..%d]-(connected:GoldenRecord)
                WHERE r.type IN ['SPOUSE', 'CHILD', 'PARENT', 'SIBLING']
                   OR (connected.family_id = start.family_id AND connected.family_id IS NOT NULL)
                WITH DISTINCT start, connected, relationships(path) AS rels
                UNWIND rels AS rel
                WITH DISTINCT start, connected, head(collect(rel)) AS rel
                RETURN DISTINCT
                  id(start) AS startId,
                  start.gr_id AS startGrId,
                  start.full_name AS startName,
                  start.age AS startAge,
                  start.gender AS startGender,
                  id(connected) AS connectedId,
                  connected.gr_id AS connectedGrId,
                  connected.full_name AS connectedName,
                  connected.age AS connectedAge,
                  connected.gender AS connectedGender,
                  rel.type AS relationshipType,
                  rel.weight AS weight
                """, matchProperty, depth);

            Result result = session.run(cypher, Map.of("identifier", identifier));
            
            Set<Map<String, Object>> nodes = new LinkedHashSet<>();
            List<Map<String, Object>> links = new ArrayList<>();
            
            while (result.hasNext()) {
                org.neo4j.driver.Record record = result.next();
                
                // Add start node
                Map<String, Object> startNode = new HashMap<>();
                startNode.put("id", record.get("startId").asLong());
                startNode.put("gr_id", record.get("startGrId").isNull() ? null : record.get("startGrId").asString());
                startNode.put("label", record.get("startName").isNull() ? "Unknown" : record.get("startName").asString());
                startNode.put("name", record.get("startName").isNull() ? "Unknown" : record.get("startName").asString());
                startNode.put("age", record.get("startAge").isNull() ? null : record.get("startAge").asInt());
                startNode.put("gender", record.get("startGender").isNull() ? null : record.get("startGender").asString());
                nodes.add(startNode);
                
                // Add connected node
                Map<String, Object> connectedNode = new HashMap<>();
                connectedNode.put("id", record.get("connectedId").asLong());
                connectedNode.put("gr_id", record.get("connectedGrId").isNull() ? null : record.get("connectedGrId").asString());
                connectedNode.put("label", record.get("connectedName").isNull() ? "Unknown" : record.get("connectedName").asString());
                connectedNode.put("name", record.get("connectedName").isNull() ? "Unknown" : record.get("connectedName").asString());
                connectedNode.put("age", record.get("connectedAge").isNull() ? null : record.get("connectedAge").asInt());
                connectedNode.put("gender", record.get("connectedGender").isNull() ? null : record.get("connectedGender").asString());
                nodes.add(connectedNode);
                
                // Add link with relationship type
                Map<String, Object> link = new HashMap<>();
                link.put("source", record.get("startId").asLong());
                link.put("target", record.get("connectedId").asLong());
                String relType = record.get("relationshipType").isNull() ? "RELATED" : record.get("relationshipType").asString();
                link.put("relationship_type", relType);
                link.put("label", relType);
                link.put("type", relType);
                link.put("relationship", relType);
                if (!record.get("weight").isNull()) {
                    link.put("weight", record.get("weight").asDouble());
                }
                links.add(link);
            }
            
            // If no results found, return at least the starting node
            if (nodes.isEmpty()) {
                // Try to get the starting node itself
                String nodeQuery = String.format("""
                    MATCH (start:GoldenRecord {%s: $identifier})
                    RETURN 
                      id(start) AS nodeId,
                      start.gr_id AS grId,
                      start.full_name AS name,
                      start.age AS age,
                      start.gender AS gender
                    LIMIT 1
                    """, matchProperty);
                
                Result nodeResult = session.run(nodeQuery, Map.of("identifier", identifier));
                if (nodeResult.hasNext()) {
                    org.neo4j.driver.Record record = nodeResult.next();
                    Map<String, Object> node = new HashMap<>();
                    node.put("id", record.get("nodeId").asLong());
                    node.put("gr_id", record.get("grId").isNull() ? null : record.get("grId").asString());
                    String name = record.get("name").isNull() ? "Unknown" : record.get("name").asString();
                    node.put("label", name);
                    node.put("name", name);
                    node.put("age", record.get("age").isNull() ? null : record.get("age").asInt());
                    node.put("gender", record.get("gender").isNull() ? null : record.get("gender").asString());
                    nodes.add(node);
                }
            }
            
            return Map.of(
                "nodes", new ArrayList<>(nodes),
                "links", links
            );
        } catch (Exception e) {
            // Log error and return empty graph
            System.err.println("Error querying Neo4j: " + e.getMessage());
            e.printStackTrace();
            return Map.of(
                "nodes", new ArrayList<>(),
                "links", new ArrayList<>()
            );
        }
    }

    /**
     * Get relationship types legend/mapping for frontend display
     */
    public Map<String, Object> getRelationshipTypes() {
        return Map.of(
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
    }

    /**
     * Cleanup driver on shutdown
     */
    public void close() {
        if (driver != null) {
            driver.close();
        }
    }
}

