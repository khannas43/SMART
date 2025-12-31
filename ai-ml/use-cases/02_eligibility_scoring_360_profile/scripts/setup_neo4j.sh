#!/bin/bash
# Neo4j Setup Script for Eligibility Scoring & 360° Profiles
# Sets up Neo4j database and initializes graph structure

echo "=========================================="
echo "Neo4j Setup for Graph Clustering"
echo "=========================================="

# Check if Neo4j is running
echo ""
echo "Checking Neo4j connection..."
if command -v cypher-shell &> /dev/null; then
    echo "✅ cypher-shell found"
else
    echo "⚠️  cypher-shell not found. Make sure Neo4j Desktop is running."
    echo "   Neo4j Desktop should be installed and running."
    exit 1
fi

# Test connection
echo ""
echo "Testing Neo4j connection..."
NEO4J_URI="${NEO4J_URI:-bolt://localhost:7687}"
NEO4J_USER="${NEO4J_USER:-neo4j}"
NEO4J_PASSWORD="${NEO4J_PASSWORD:-neo4j}"

if cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1" &> /dev/null; then
    echo "✅ Neo4j connection successful"
else
    echo "❌ Neo4j connection failed"
    echo ""
    echo "Please ensure:"
    echo "  1. Neo4j Desktop is installed and running"
    echo "  2. A database is created and started"
    echo "  3. Default password is set (or update NEO4J_PASSWORD)"
    echo ""
    echo "To set password in Neo4j Desktop:"
    echo "  - Open Neo4j Desktop"
    echo "  - Click on your database"
    echo "  - Click 'Open' to open Neo4j Browser"
    echo "  - Set password when prompted"
    exit 1
fi

# Create indexes
echo ""
echo "Creating Neo4j indexes..."
cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" << 'EOF'
CREATE INDEX gr_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.gr_id);
CREATE INDEX family_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.family_id);
CREATE INDEX cluster_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.cluster_id);
EOF

if [ $? -eq 0 ]; then
    echo "✅ Indexes created"
else
    echo "⚠️  Index creation had issues (may already exist)"
fi

# Check if GDS (Graph Data Science) library is available
echo ""
echo "Checking for GDS (Graph Data Science) library..."
GDS_CHECK=$(cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "CALL gds.version() YIELD version RETURN version" 2>&1)

if echo "$GDS_CHECK" | grep -q "version"; then
    echo "✅ GDS library is available"
    echo "   Version: $(echo "$GDS_CHECK" | grep -oP 'version.*' | head -1)"
else
    echo "⚠️  GDS library not found"
    echo "   Community detection will use fallback methods"
    echo "   To install GDS:"
    echo "   1. Open Neo4j Desktop"
    echo "   2. Click on your database"
    echo "   3. Go to 'Plugins' tab"
    echo "   4. Install 'Graph Data Science' plugin"
fi

echo ""
echo "=========================================="
echo "✅ Neo4j setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Update Neo4j password in config/db_config.yaml if needed"
echo "  2. Run graph clustering: cd src && python graph_clustering_neo4j.py"

