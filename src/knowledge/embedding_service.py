"""
Embedding Service for vector embeddings and semantic search.

This module provides functionality for generating and searching
vector embeddings for semantic similarity.
"""

class EmbeddingService:
    """
    Service for managing vector embeddings and semantic search.
    
    Responsibilities:
    - Generate vector embeddings for text content
    - Perform semantic similarity search
    - Maintain vector representations of knowledge entities
    - Map between vector search results and knowledge entities
    """
    
    def __init__(self):
        """
        Initialize the embedding service with mock data for Phase 1.
        
        In a real implementation, this would connect to a vector database
        like Qdrant, Pinecone, or Weaviate.
        """
        # Mock embeddings for Phase 1
        self.mock_vectors = {
            "knowledge_graph": [0.1, 0.2, 0.3],  # Simplified 3D vectors for demo
            "semantic_search": [0.15, 0.25, 0.35],
            "vector_embeddings": [0.2, 0.3, 0.4],
            "graph_database": [0.05, 0.15, 0.25]
        }
        
        # Mock search results for specific queries
        self.mock_results = {
            "knowledge graph": [
                {
                    "id": "knowledge_graph",
                    "score": 0.95,
                    "text": "A knowledge graph is a network-based representation of knowledge that uses nodes to represent entities and edges to represent relationships between entities.",
                    "source": "Internal Knowledge Base"
                },
                {
                    "id": "graph_database",
                    "score": 0.75,
                    "text": "A graph database is a specialized database optimized for storing and querying data represented as a graph with nodes, edges, and properties.",
                    "source": "Internal Knowledge Base"
                }
            ],
            "semantic search": [
                {
                    "id": "semantic_search",
                    "score": 0.98,
                    "text": "Semantic search is a search technique that understands the contextual meaning of terms to improve accuracy of search results beyond keyword matching.",
                    "source": "Internal Knowledge Base"
                },
                {
                    "id": "vector_embeddings",
                    "score": 0.82,
                    "text": "Vector embeddings are numerical representations of concepts that capture semantic meaning in a high-dimensional space, allowing similarity measurements between concepts.",
                    "source": "Internal Knowledge Base"
                }
            ],
            "vector embeddings": [
                {
                    "id": "vector_embeddings",
                    "score": 0.97,
                    "text": "Vector embeddings are numerical representations of concepts that capture semantic meaning in a high-dimensional space, allowing similarity measurements between concepts.",
                    "source": "Internal Knowledge Base"
                },
                {
                    "id": "semantic_search",
                    "score": 0.80,
                    "text": "Semantic search is a search technique that understands the contextual meaning of terms to improve accuracy of search results beyond keyword matching.",
                    "source": "Internal Knowledge Base"
                }
            ]
        }
    
    def generate_embedding(self, text):
        """
        Generate vector embedding for a text string.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Vector embedding (simplified 3D vector for Phase 1)
        """
        # Mock implementation for Phase 1
        # In a real implementation, this would use a model like BERT or OpenAI embeddings
        
        # Simple mock function that pretends to create an embedding
        # In reality, this would call a model or API
        
        # Use the first 3 letters to generate a mock vector
        if not text:
            return [0.0, 0.0, 0.0]
            
        chars = text.lower()[:3]
        vector = [ord(c) / 100 for c in chars]
        
        # Pad to ensure we have 3 dimensions
        while len(vector) < 3:
            vector.append(0.0)
            
        return vector[:3]  # Return only first 3 dimensions
    
    def search(self, query, top_k=5, filters=None):
        """
        Perform semantic search using vector embeddings.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional filters to apply to search
            
        Returns:
            List of search results with relevance scores
        """
        # Mock implementation for Phase 1
        # In a real implementation, this would query a vector database
        
        # Convert query to lowercase for matching
        query_lower = query.lower()
        
        # Check if we have pre-defined results for this query
        for key, results in self.mock_results.items():
            if key in query_lower:
                # Return a copy of the results to avoid modifying the original
                return results[:top_k]
        
        # If no pre-defined results, generate some basic ones
        # based on simple string matching
        
        # Define some basic knowledge entries
        knowledge_entries = [
            {
                "id": "knowledge_graph",
                "text": "A knowledge graph is a network-based representation of knowledge that uses nodes to represent entities and edges to represent relationships between entities.",
                "source": "Internal Knowledge Base"
            },
            {
                "id": "semantic_search",
                "text": "Semantic search is a search technique that understands the contextual meaning of terms to improve accuracy of search results beyond keyword matching.",
                "source": "Internal Knowledge Base"
            },
            {
                "id": "vector_embeddings",
                "text": "Vector embeddings are numerical representations of concepts that capture semantic meaning in a high-dimensional space, allowing similarity measurements between concepts.",
                "source": "Internal Knowledge Base"
            },
            {
                "id": "graph_database",
                "text": "A graph database is a specialized database optimized for storing and querying data represented as a graph with nodes, edges, and properties.",
                "source": "Internal Knowledge Base"
            }
        ]
        
        # Calculate a simple relevance score based on word overlap
        results = []
        query_words = set(query_lower.split())
        
        for entry in knowledge_entries:
            text_lower = entry["text"].lower()
            text_words = set(text_lower.split())
            
            # Count overlapping words
            overlap = len(query_words.intersection(text_words))
            
            # Calculate a mock score
            if len(query_words) > 0:
                score = min(0.95, overlap / len(query_words))
            else:
                score = 0.0
                
            # Only include if there's some relevance
            if score > 0:
                results.append({
                    "id": entry["id"],
                    "score": score,
                    "text": entry["text"],
                    "source": entry["source"]
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k] 