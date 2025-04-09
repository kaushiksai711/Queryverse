"""
Mock Qdrant connector for vector database functionality.

This module provides a mock implementation of a Qdrant connector
for Phase 1, which will be replaced with a real connector in Phase 2.
"""

class QdrantConnector:
    """
    Mock connector for Qdrant vector database.
    
    Responsibilities:
    - Provide a mock interface for Qdrant operations
    - Simulate vector similarity search with mock data
    - Implement a basic API that mirrors the real Qdrant API
    """
    
    def __init__(self, url=None, api_key=None, collection_name="knowledge"):
        """
        Initialize the mock Qdrant connector.
        
        Args:
            url: Mock service URL
            api_key: Mock API key
            collection_name: Mock collection name
        """
        self.url = url or "mock://localhost:6333"
        self.api_key = api_key
        self.collection_name = collection_name
        self.connected = False
        
        # Mock vectors for entities (simplified 3D vectors)
        self.vectors = {
            "knowledge_graph": [0.1, 0.2, 0.3],
            "semantic_search": [0.15, 0.25, 0.35],
            "vector_embeddings": [0.2, 0.3, 0.4],
            "graph_database": [0.05, 0.15, 0.25],
            "neo4j": [0.12, 0.22, 0.32],
            "qdrant": [0.18, 0.28, 0.38]
        }
        
        # Metadata for each vector
        self.metadata = {
            "knowledge_graph": {
                "id": "knowledge_graph",
                "name": "Knowledge Graph",
                "description": "A knowledge graph is a network-based representation of knowledge.",
                "category": "concept"
            },
            "semantic_search": {
                "id": "semantic_search",
                "name": "Semantic Search",
                "description": "Semantic search understands the contextual meaning of terms.",
                "category": "technique"
            },
            "vector_embeddings": {
                "id": "vector_embeddings",
                "name": "Vector Embeddings",
                "description": "Vector embeddings are numerical representations of concepts.",
                "category": "technique"
            },
            "graph_database": {
                "id": "graph_database",
                "name": "Graph Database",
                "description": "A graph database stores data in a graph structure.",
                "category": "technology"
            },
            "neo4j": {
                "id": "neo4j",
                "name": "Neo4j",
                "description": "Neo4j is a popular graph database management system.",
                "category": "technology"
            },
            "qdrant": {
                "id": "qdrant",
                "name": "Qdrant",
                "description": "Qdrant is a vector similarity search engine.",
                "category": "technology"
            }
        }
        
        # Log initialization
        print(f"[Mock] Initialized Qdrant connector to {self.url} with collection {self.collection_name}")
    
    def connect(self):
        """
        Simulate connecting to Qdrant.
        
        Returns:
            True if connection successful
        """
        # In Phase 1, this just sets a flag
        self.connected = True
        print("[Mock] Connected to Qdrant")
        return True
    
    def disconnect(self):
        """
        Simulate disconnecting from Qdrant.
        """
        self.connected = False
        print("[Mock] Disconnected from Qdrant")
    
    def search(self, vector, top_k=5, filters=None):
        """
        Simulate vector similarity search.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of search results with similarity scores
        """
        if not self.connected:
            print("[Mock] Warning: Not connected to Qdrant")
            return []
        
        # Log the search
        print(f"[Mock] Searching with vector: {vector}")
        if filters:
            print(f"[Mock] With filters: {filters}")
        
        # Calculate mock similarity scores
        # In a real implementation, this would use cosine similarity or other distance metrics
        results = []
        for entity_id, entity_vector in self.vectors.items():
            # Skip if it doesn't pass filters
            if not self._passes_filters(entity_id, filters):
                continue
                
            # Calculate a simple similarity score
            similarity = self._calculate_similarity(vector, entity_vector)
            
            # Add to results
            if similarity > 0:
                results.append({
                    "id": entity_id,
                    "score": similarity,
                    "metadata": self.metadata.get(entity_id, {})
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top k results
        return results[:top_k]
    
    def _calculate_similarity(self, vec1, vec2):
        """
        Calculate a mock similarity score between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score between 0 and 1
        """
        # Very simple mock similarity for Phase 1
        # In a real implementation, this would use cosine similarity
        
        # Ensure vectors have the same length
        min_length = min(len(vec1), len(vec2))
        vec1 = vec1[:min_length]
        vec2 = vec2[:min_length]
        
        # Calculate a simple similarity based on vector difference
        total_diff = sum(abs(a - b) for a, b in zip(vec1, vec2))
        max_possible_diff = min_length  # Assuming values between 0 and 1
        
        # Convert difference to similarity (1 - normalized difference)
        similarity = 1.0 - (total_diff / max_possible_diff)
        
        # Ensure it's between 0 and 1
        return max(0.0, min(1.0, similarity))
    
    def _passes_filters(self, entity_id, filters):
        """
        Check if an entity passes the specified filters.
        
        Args:
            entity_id: Entity identifier
            filters: Filters to apply
            
        Returns:
            True if the entity passes all filters
        """
        # If no filters, everything passes
        if not filters:
            return True
            
        # Get entity metadata
        metadata = self.metadata.get(entity_id, {})
        
        # Check each filter
        for field, value in filters.items():
            if field not in metadata:
                return False
                
            if isinstance(value, list):
                # For list values, check if any match
                if metadata[field] not in value:
                    return False
            else:
                # For single values, check exact match
                if metadata[field] != value:
                    return False
        
        # If we get here, all filters passed
        return True
    
    def upsert(self, id, vector, metadata=None):
        """
        Simulate upserting a vector to the collection.
        
        Args:
            id: Entity identifier
            vector: Vector to store
            metadata: Associated metadata
            
        Returns:
            Success flag
        """
        if not self.connected:
            print("[Mock] Warning: Not connected to Qdrant")
            return False
        
        # Log the operation
        print(f"[Mock] Upserting vector for ID: {id}")
        
        # Store the vector and metadata
        self.vectors[id] = vector
        if metadata:
            self.metadata[id] = metadata
        
        return True 