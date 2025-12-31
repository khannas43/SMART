"""
Neo4j Database Connector for SMART Platform
Connects to Neo4j graph database using neo4j driver
"""

from neo4j import GraphDatabase
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Neo4jConnector:
    """Neo4j graph database connector"""
    
    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "neo4j",
        database: str = "neo4j"
    ):
        """
        Initialize Neo4j connector
        
        Args:
            uri: Neo4j bolt URI
            user: Neo4j username
            password: Neo4j password
            database: Database name (default: neo4j)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
    
    def connect(self):
        """Establish Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            print(f"✅ Connected to Neo4j: {self.uri}/{self.database}")
            return self.driver
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            raise
    
    def disconnect(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.driver = None
            print("Neo4j connection closed")
    
    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            
        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> int:
        """
        Execute a write query (CREATE, UPDATE, DELETE) and return count
        
        Args:
            query: Cypher query string
            parameters: Query parameters dictionary
            
        Returns:
            Number of records affected
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        
        with self.driver.session(database=self.database) as session:
            result = session.run(query, parameters or {})
            summary = result.consume()
            return summary.counters.nodes_created + summary.counters.nodes_deleted + \
                   summary.counters.relationships_created + summary.counters.relationships_deleted
    
    def clear_database(self):
        """Clear all nodes and relationships (use with caution!)"""
        query = "MATCH (n) DETACH DELETE n"
        count = self.execute_write(query)
        print(f"✅ Cleared database: deleted all nodes and relationships")
        return count
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        node_query = "MATCH (n) RETURN count(n) as node_count"
        rel_query = "MATCH ()-[r]->() RETURN count(r) as rel_count"
        
        nodes = self.execute_query(node_query)[0]['node_count']
        rels = self.execute_query(rel_query)[0]['rel_count']
        
        return {
            'nodes': nodes,
            'relationships': rels
        }
    
    def create_indexes(self):
        """Create common indexes for performance"""
        indexes = [
            "CREATE INDEX gr_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.gr_id)",
            "CREATE INDEX family_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.family_id)",
            "CREATE INDEX cluster_id_index IF NOT EXISTS FOR (n:GoldenRecord) ON (n.cluster_id)"
        ]
        
        for index_query in indexes:
            try:
                self.execute_write(index_query)
            except Exception as e:
                logger.warning(f"Index creation warning: {e}")
        
        print("✅ Neo4j indexes created")

