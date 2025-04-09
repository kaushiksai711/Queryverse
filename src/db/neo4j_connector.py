"""
Mock Neo4j connector for graph database functionality.

This module provides a mock implementation of a Neo4j connector
for Phase 1, which will be replaced with a real connector in Phase 2.
"""

class Neo4jConnector:
    """
    Mock connector for Neo4j graph database.
    
    Responsibilities:
    - Provide a mock interface for Neo4j operations
    - Simulate graph database queries with mock data
    - Implement a basic API that mirrors the real Neo4j API
    """
    
    def __init__(self, uri=None, user=None, password=None):
        """
        Initialize the mock Neo4j connector.
        
        Args:
            uri: Mock database URI
            user: Mock username
            password: Mock password
        """
        self.uri = uri or "mock://localhost:7687"
        self.user = user or "neo4j"
        self.password = password or "password"
        self.connected = False
        
        # Log initialization
        print(f"[Mock] Initialized Neo4j connector to {self.uri}")
    
    def connect(self):
        """
        Simulate connecting to Neo4j.
        
        Returns:
            True if connection successful
        """
        # In Phase 1, this just sets a flag
        self.connected = True
        print("[Mock] Connected to Neo4j")
        return True
    
    def disconnect(self):
        """
        Simulate disconnecting from Neo4j.
        """
        self.connected = False
        print("[Mock] Disconnected from Neo4j")
    
    def execute_query(self, query, params=None):
        """
        Simulate executing a Cypher query.
        
        Args:
            query: Cypher query string
            params: Optional parameters for the query
            
        Returns:
            Mock query results
        """
        if not self.connected:
            print("[Mock] Warning: Not connected to Neo4j")
            return []
        
        # Log the query
        print(f"[Mock] Executing query: {query}")
        if params:
            print(f"[Mock] With parameters: {params}")
        
        # Simulate different query types based on simple matching
        query_lower = query.lower()
        
        # Mock MATCH query for entities
        if "match (n:" in query_lower and "return n" in query_lower:
            label = self._extract_label(query)
            return self._mock_match_nodes(label)
        
        # Mock MATCH query for relationships
        if "match (a)-[r:" in query_lower:
            rel_type = self._extract_relationship_type(query)
            return self._mock_match_relationships(rel_type)
        
        # Default empty result
        return []
    
    def _extract_label(self, query):
        """
        Extract node label from a Cypher query.
        
        Args:
            query: Cypher query string
            
        Returns:
            Extracted label or None
        """
        # Very simple extraction for Phase 1
        query_lower = query.lower()
        start_idx = query_lower.find("match (n:") + 8
        end_idx = query_lower.find(")", start_idx)
        
        if start_idx >= 8 and end_idx > start_idx:
            return query[start_idx:end_idx]
        
        return None
    
    def _extract_relationship_type(self, query):
        """
        Extract relationship type from a Cypher query.
        
        Args:
            query: Cypher query string
            
        Returns:
            Extracted relationship type or None
        """
        # Very simple extraction for Phase 1
        query_lower = query.lower()
        start_idx = query_lower.find("[r:") + 3
        end_idx = query_lower.find("]", start_idx)
        
        if start_idx >= 3 and end_idx > start_idx:
            return query[start_idx:end_idx]
        
        return None
    
    def _mock_match_nodes(self, label):
        """
        Generate mock results for a node MATCH query.
        
        Args:
            label: Node label to match
            
        Returns:
            List of mock nodes
        """
        if not label:
            return []
            
        # Convert label to friendly format for comparison
        label = label.strip().lower()
        
        # Mock data for different entity types
        if label == "concept" or label == "knowledge":
            return [
                {"id": "knowledge_graph", "name": "Knowledge Graph", "type": "concept"},
                {"id": "semantic_search", "name": "Semantic Search", "type": "concept"},
                {"id": "vector_embeddings", "name": "Vector Embeddings", "type": "concept"}
            ]
        elif label == "technology":
            return [
                {"id": "neo4j", "name": "Neo4j", "type": "technology"},
                {"id": "qdrant", "name": "Qdrant", "type": "technology"}
            ]
        
        # Default empty result
        return []
    
    def _mock_match_relationships(self, rel_type):
        """
        Generate mock results for a relationship MATCH query.
        
        Args:
            rel_type: Relationship type to match
            
        Returns:
            List of mock relationships
        """
        if not rel_type:
            return []
            
        # Convert type to friendly format for comparison
        rel_type = rel_type.strip().upper()
        
        # Mock data for different relationship types
        if rel_type == "RELATED_TO":
            return [
                {
                    "source": {"id": "knowledge_graph", "name": "Knowledge Graph"},
                    "relationship": {"type": "RELATED_TO", "strength": 0.9},
                    "target": {"id": "semantic_search", "name": "Semantic Search"}
                },
                {
                    "source": {"id": "semantic_search", "name": "Semantic Search"},
                    "relationship": {"type": "RELATED_TO", "strength": 0.9},
                    "target": {"id": "knowledge_graph", "name": "Knowledge Graph"}
                }
            ]
        elif rel_type == "USES":
            return [
                {
                    "source": {"id": "knowledge_graph", "name": "Knowledge Graph"},
                    "relationship": {"type": "USES", "required": True},
                    "target": {"id": "graph_database", "name": "Graph Database"}
                },
                {
                    "source": {"id": "semantic_search", "name": "Semantic Search"},
                    "relationship": {"type": "USES", "strength": 0.95},
                    "target": {"id": "vector_embeddings", "name": "Vector Embeddings"}
                }
            ]
        
        # Default empty result
        return [] 