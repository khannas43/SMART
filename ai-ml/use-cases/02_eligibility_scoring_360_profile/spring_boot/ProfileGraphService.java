package com.smart.platform.aiml.profile360.service;

import org.neo4j.driver.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Service to fetch graph data from Neo4j for frontend visualization
 */
@Service
public class ProfileGraphService {

    @Value("${neo4j.uri:bolt://localhost:7687}")
    private String neo4jUri;

    @Value("${neo4j.user:neo4j}")
    private String neo4jUser;

    @Value("${neo4j.password:neo4j}")
    private String neo4jPassword;

    @Value("${neo4j.database:neo4j}")
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
     * Returns data in format compatible with react-force-graph or vis-network
     * 
     * @param grId Golden Record ID
     * @param depth Depth of relationships
     * @return Map with "nodes" and "links" arrays
     */
    public Map<String, Object> getFamilyNetwork(UUID grId, int depth) {
        try (Session session = getDriver().session(SessionConfig.forDatabase(neo4jDatabase))) {
            String cypher = """
                MATCH path = (start:GoldenRecord {gr_id: $grId})-[r:RELATED_TO*1..%d]-(connected:GoldenRecord)
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
                """.formatted(depth);

            Result result = session.run(cypher, Map.of("grId", grId.toString()));
            
            Set<Map<String, Object>> nodes = new LinkedHashSet<>();
            List<Map<String, Object>> links = new ArrayList<>();
            
            while (result.hasNext()) {
                Record record = result.next();
                
                // Add start node
                Map<String, Object> startNode = Map.of(
                    "id", record.get("startId").asLong(),
                    "gr_id", record.get("startGrId").asString(),
                    "label", record.get("startName").asString("Unknown"),
                    "name", record.get("startName").asString("Unknown"),
                    "age", record.get("startAge").isNull() ? null : record.get("startAge").asInt(),
                    "gender", record.get("startGender").isNull() ? null : record.get("startGender").asString()
                );
                nodes.add(startNode);
                
                // Add connected node
                Map<String, Object> connectedNode = Map.of(
                    "id", record.get("connectedId").asLong(),
                    "gr_id", record.get("connectedGrId").asString(),
                    "label", record.get("connectedName").asString("Unknown"),
                    "name", record.get("connectedName").asString("Unknown"),
                    "age", record.get("connectedAge").isNull() ? null : record.get("connectedAge").asInt(),
                    "gender", record.get("connectedGender").isNull() ? null : record.get("connectedGender").asString()
                );
                nodes.add(connectedNode);
                
                // Add link with relationship type
                Map<String, Object> link = new HashMap<>();
                link.put("source", record.get("startId").asLong());
                link.put("target", record.get("connectedId").asLong());
                link.put("relationship_type", record.get("relationshipType").asString());
                link.put("label", record.get("relationshipType").asString());
                link.put("type", record.get("relationshipType").asString());
                if (!record.get("weight").isNull()) {
                    link.put("weight", record.get("weight").asDouble());
                }
                links.add(link);
            }
            
            return Map.of(
                "nodes", new ArrayList<>(nodes),
                "links", links
            );
        }
    }

    /**
     * Get network graph with optional relationship type filter
     */
    public Map<String, Object> getNetwork(UUID grId, List<String> relationshipTypes) {
        try (Session session = getDriver().session(SessionConfig.forDatabase(neo4jDatabase))) {
            String typeFilter = relationshipTypes != null && !relationshipTypes.isEmpty()
                ? "AND r.type IN " + relationshipTypes.stream()
                    .map(t -> "'" + t + "'")
                    .collect(Collectors.joining(", ", "[", "]"))
                : "";
            
            String cypher = """
                MATCH (start:GoldenRecord {gr_id: $grId})-[r:RELATED_TO]-(connected:GoldenRecord)
                WHERE 1=1 %s
                RETURN
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
                  r.type AS relationshipType,
                  r.weight AS weight
                """.formatted(typeFilter);

            Result result = session.run(cypher, Map.of("grId", grId.toString()));
            
            Set<Map<String, Object>> nodes = new LinkedHashSet<>();
            List<Map<String, Object>> links = new ArrayList<>();
            
            while (result.hasNext()) {
                Record record = result.next();
                
                // Similar node and link building as above
                Map<String, Object> startNode = Map.of(
                    "id", record.get("startId").asLong(),
                    "gr_id", record.get("startGrId").asString(),
                    "label", record.get("startName").asString("Unknown"),
                    "name", record.get("startName").asString("Unknown"),
                    "age", record.get("startAge").isNull() ? null : record.get("startAge").asInt(),
                    "gender", record.get("startGender").isNull() ? null : record.get("startGender").asString()
                );
                nodes.add(startNode);
                
                Map<String, Object> connectedNode = Map.of(
                    "id", record.get("connectedId").asLong(),
                    "gr_id", record.get("connectedGrId").asString(),
                    "label", record.get("connectedName").asString("Unknown"),
                    "name", record.get("connectedName").asString("Unknown"),
                    "age", record.get("connectedAge").isNull() ? null : record.get("connectedAge").asInt(),
                    "gender", record.get("connectedGender").isNull() ? null : record.get("connectedGender").asString()
                );
                nodes.add(connectedNode);
                
                Map<String, Object> link = new HashMap<>();
                link.put("source", record.get("startId").asLong());
                link.put("target", record.get("connectedId").asLong());
                link.put("relationship_type", record.get("relationshipType").asString());
                link.put("label", record.get("relationshipType").asString());
                link.put("type", record.get("relationshipType").asString());
                if (!record.get("weight").isNull()) {
                    link.put("weight", record.get("weight").asDouble());
                }
                links.add(link);
            }
            
            return Map.of(
                "nodes", new ArrayList<>(nodes),
                "links", links
            );
        }
    }
}

