"""
Retrieval Agent for fetching information from knowledge bases.

This module contains the implementation of the retrieval agent
which is responsible for searching the knowledge base to find
relevant information for user queries.
"""

class RetrievalAgent:
    """
    Agent responsible for retrieving information from knowledge bases.
    
    Responsibilities:
    - Search the knowledge graph for relevant entities
    - Perform semantic search using vector embeddings
    - Evaluate confidence in retrieval results
    - Handle simple query rewrites to improve search results
    """
    
    def __init__(self, graph_manager, embedding_service):
        """
        Initialize the retrieval agent with required components.
        
        Args:
            graph_manager: Manager for graph database operations
            embedding_service: Service for vector embeddings and search
        """
        self.graph_manager = graph_manager
        self.embedding_service = embedding_service
    
    def retrieve(self, query, context=None):
        """
        Retrieve information relevant to the interpreted query.
        
        Args:
            query: Interpreted query object from query interpreter
            context: Optional context information
            
        Returns:
            Dictionary containing retrieval results and metadata
        """
        # Default empty context if none provided
        if context is None:
            context = {}
        
        # For Phase 1, we'll implement two basic search strategies
        
        # 1. Vector-based semantic search
        semantic_results = self._semantic_search(query)
        
        # 2. Graph-based entity search
        graph_results = self._graph_search(query)
        
        # Combine results (simple implementation for Phase 1)
        combined_results = self._combine_results(semantic_results, graph_results)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(combined_results)
        
        # Return consolidated results
        return {
            'results': combined_results,
            'confidence': confidence,
            'sources': self._extract_sources(combined_results),
            'query': query
        }
    
    def _semantic_search(self, query):
        """
        Perform semantic search using vector embeddings.
        
        Args:
            query: Interpreted query object
            
        Returns:
            List of semantic search results
        """
        # In Phase 1, this will use mock data
        query_text = query.get('text', '')
        
        # Mock implementation
        return self.embedding_service.search(query_text, top_k=5)
    
    def _graph_search(self, query):
        """
        Search for entities in the knowledge graph.
        
        Args:
            query: Interpreted query object
            
        Returns:
            List of graph search results
        """
        # In Phase 1, this will use mock data
        entities = query.get('entities', [])
        
        # Mock implementation
        results = []
        for entity in entities:
            graph_result = self.graph_manager.find_entity(entity)
            if graph_result:
                results.append(graph_result)
        
        return results
    
    def _combine_results(self, semantic_results, graph_results):
        """
        Combine results from different search strategies.
        
        Args:
            semantic_results: Results from semantic search
            graph_results: Results from graph search
            
        Returns:
            Combined and ranked results
        """
        # Simple combination for Phase 1
        combined = []
        
        # Add graph results first (usually more precise)
        combined.extend(graph_results)
        
        # Add semantic results that aren't duplicates
        existing_ids = {r.get('id') for r in combined if 'id' in r}
        for result in semantic_results:
            if result.get('id') not in existing_ids:
                combined.append(result)
        
        return combined
    
    def _calculate_confidence(self, results):
        """
        Calculate a confidence score for the retrieval results.
        
        Args:
            results: Combined search results
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple implementation for Phase 1
        if not results:
            return 0.0
        
        # Average the relevance scores of top 3 results
        top_results = results[:3]
        scores = [r.get('score', 0) for r in top_results if 'score' in r]
        
        if not scores:
            return 0.3  # Default low confidence if no scores available
        
        return sum(scores) / len(scores)
    
    def _extract_sources(self, results):
        """
        Extract source information from results for attribution.
        
        Args:
            results: Combined search results
            
        Returns:
            List of source information
        """
        sources = []
        for result in results:
            if 'source' in result:
                source = result['source']
                if source not in sources:
                    sources.append(source)
        
        return sources 