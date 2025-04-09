"""
Graph Manager for graph database operations.

This module provides an interface for interacting with the graph database,
which stores knowledge as connected entities with relationships.
"""

class GraphManager:
    """
    Manager for graph database operations.
    
    Responsibilities:
    - Find entities in the knowledge graph
    - Retrieve entity properties and relationships
    - Find related entities through graph traversal
    - Perform basic graph queries
    """
    
    def __init__(self):
        """
        Initialize the graph manager with mock data for Phase 1.
        
        In a real implementation, this would connect to a Neo4j instance.
        """
        # Mock knowledge graph for Phase 1
        self.entities = {
            "knowledge_graph": {
                "id": "knowledge_graph",
                "name": "Knowledge Graph",
                "description": "A knowledge graph is a network-based representation of knowledge that uses nodes to represent entities and edges to represent relationships between entities.",
                "properties": {
                    "use_cases": ["Semantic search", "Question answering", "Data integration"],
                    "technologies": ["Neo4j", "GraphDB", "Amazon Neptune"]
                },
                "relationships": [
                    {"type": "RELATED_TO", "target": "semantic_search", "properties": {"strength": 0.9}},
                    {"type": "USES", "target": "graph_database", "properties": {"required": True}}
                ],
                "source": "Internal Knowledge Base"
            },
            "semantic_search": {
                "id": "semantic_search",
                "name": "Semantic Search",
                "description": "Semantic search is a search technique that understands the contextual meaning of terms to improve accuracy of search results beyond keyword matching.",
                "properties": {
                    "components": ["Vector embeddings", "Natural language understanding"],
                    "advantages": ["Better relevance", "Handles synonyms", "Understands context"]
                },
                "relationships": [
                    {"type": "USES", "target": "vector_embeddings", "properties": {"strength": 0.95}},
                    {"type": "RELATED_TO", "target": "knowledge_graph", "properties": {"strength": 0.9}}
                ],
                "source": "Internal Knowledge Base"
            },
            "vector_embeddings": {
                "id": "vector_embeddings",
                "name": "Vector Embeddings",
                "description": "Vector embeddings are numerical representations of concepts that capture semantic meaning in a high-dimensional space, allowing similarity measurements between concepts.",
                "properties": {
                    "models": ["Word2Vec", "BERT", "USE", "OpenAI Embeddings"],
                    "dimensions": "Typically 300-1536"
                },
                "relationships": [
                    {"type": "USED_BY", "target": "semantic_search", "properties": {"strength": 0.95}}
                ],
                "source": "Internal Knowledge Base"
            },
            "graph_database": {
                "id": "graph_database",
                "name": "Graph Database",
                "description": "A graph database is a specialized database optimized for storing and querying data represented as a graph with nodes, edges, and properties.",
                "properties": {
                    "examples": ["Neo4j", "Amazon Neptune", "JanusGraph"],
                    "query_languages": ["Cypher", "Gremlin", "SPARQL"]
                },
                "relationships": [
                    {"type": "USED_BY", "target": "knowledge_graph", "properties": {"required": True}}
                ],
                "source": "Internal Knowledge Base"
            }
        }
    
    def find_entity(self, entity_name):
        """
        Find an entity in the knowledge graph by name.
        
        Args:
            entity_name: The name or identifier of the entity
            
        Returns:
            Entity information if found, None otherwise
        """
        # Normalize entity name for comparison
        entity_name = entity_name.lower().replace(" ", "_")
        
        # Direct lookup
        if entity_name in self.entities:
            return self.entities[entity_name]
        
        # Try to find by matching against names
        for entity_id, entity in self.entities.items():
            if entity_name in entity_id or entity_name in entity.get('name', '').lower():
                return entity
        
        return None
    
    def get_relationships(self, entity_id, relationship_types=None, direction="outgoing"):
        """
        Get relationships for an entity.
        
        Args:
            entity_id: The ID of the entity
            relationship_types: Optional list of relationship types to filter by
            direction: "outgoing", "incoming", or "both"
            
        Returns:
            List of relationship information
        """
        # Check if entity exists
        if entity_id not in self.entities:
            return []
        
        entity = self.entities[entity_id]
        relationships = []
        
        # Get outgoing relationships
        if direction in ["outgoing", "both"]:
            outgoing = entity.get('relationships', [])
            if relationship_types:
                outgoing = [r for r in outgoing if r['type'] in relationship_types]
            for rel in outgoing:
                relationships.append({
                    'source': entity_id,
                    'target': rel['target'],
                    'type': rel['type'],
                    'properties': rel.get('properties', {})
                })
        
        # Get incoming relationships
        if direction in ["incoming", "both"]:
            for src_id, src_entity in self.entities.items():
                if src_id == entity_id:
                    continue
                    
                for rel in src_entity.get('relationships', []):
                    if rel['target'] == entity_id:
                        if relationship_types and rel['type'] not in relationship_types:
                            continue
                            
                        relationships.append({
                            'source': src_id,
                            'target': entity_id,
                            'type': rel['type'],
                            'properties': rel.get('properties', {})
                        })
        
        return relationships
    
    def find_related_entities(self, entity_id, max_depth=1, relationship_types=None):
        """
        Find entities related to the given entity.
        
        Args:
            entity_id: The ID of the starting entity
            max_depth: Maximum traversal depth
            relationship_types: Optional list of relationship types to filter by
            
        Returns:
            List of related entities with relationship information
        """
        # Simple BFS implementation for Phase 1
        if entity_id not in self.entities:
            return []
            
        visited = set([entity_id])
        result = []
        queue = [(entity_id, 0)]  # (entity_id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            # Stop if we've reached max depth
            if depth >= max_depth:
                continue
            
            # Get relationships
            relationships = self.get_relationships(current_id, relationship_types, direction="both")
            
            for rel in relationships:
                other_id = rel['target'] if rel['source'] == current_id else rel['source']
                
                if other_id not in visited:
                    visited.add(other_id)
                    result.append({
                        'entity': self.entities[other_id],
                        'relationship': rel,
                        'depth': depth + 1
                    })
                    queue.append((other_id, depth + 1))
        
        return result 