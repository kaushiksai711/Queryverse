"""
Query Interpreter for understanding user queries.

This module contains the implementation of the query interpreter
which is responsible for understanding user queries and extracting
relevant entities, intents, and other information.
"""

class QueryInterpreter:
    """
    Agent responsible for interpreting user queries.
    
    Responsibilities:
    - Extract entities and keywords from user queries
    - Identify question type and intent
    - Detect query complexity
    - Prepare the query for retrieval operations
    """
    
    def __init__(self):
        """
        Initialize the query interpreter.
        """
        pass
    
    def interpret(self, query, context=None):
        """
        Interpret a user query and extract structured information.
        
        Args:
            query: Raw user query as a string
            context: Optional context information
            
        Returns:
            Dictionary containing interpreted query information
        """
        # Default empty context if none provided
        if context is None:
            context = {}
        
        # For Phase 1, implement basic interpretation
        entities = self._extract_entities(query)
        intent = self._identify_intent(query)
        
        # Create structured representation
        interpreted_query = {
            'text': query,
            'entities': entities,
            'intent': intent,
            'complexity': self._assess_complexity(query, entities)
        }
        
        return interpreted_query
    
    def _extract_entities(self, query):
        """
        Extract entities from the user query.
        
        Args:
            query: Raw user query as a string
            
        Returns:
            List of extracted entities
        """
        # Mock implementation for Phase 1
        # In a real implementation, this would use NER or similar techniques
        
        # Simple keyword extraction based on common terms in the knowledge domain
        knowledge_terms = [
            "knowledge graph", "semantic search", "vector embeddings",
            "graph database", "neo4j", "qdrant", "knowledge base",
            "chatbot", "retrieval", "research"
        ]
        
        found_entities = []
        for term in knowledge_terms:
            if term.lower() in query.lower():
                found_entities.append(term)
        
        return found_entities
    
    def _identify_intent(self, query):
        """
        Identify the intent of the user query.
        
        Args:
            query: Raw user query as a string
            
        Returns:
            Dictionary with intent type and confidence
        """
        # Mock implementation for Phase 1
        # In a real implementation, this would use a classifier
        
        # Simple rule-based intent detection
        query_lower = query.lower()
        
        if "what is" in query_lower or "definition" in query_lower:
            return {"type": "definition", "confidence": 0.8}
        elif "how does" in query_lower or "how to" in query_lower:
            return {"type": "explanation", "confidence": 0.8}
        elif "why" in query_lower:
            return {"type": "reason", "confidence": 0.7}
        elif "compare" in query_lower or "difference between" in query_lower:
            return {"type": "comparison", "confidence": 0.8}
        else:
            return {"type": "information", "confidence": 0.5}
    
    def _assess_complexity(self, query, entities):
        """
        Assess the complexity of the query.
        
        Args:
            query: Raw user query as a string
            entities: Extracted entities
            
        Returns:
            Complexity assessment ("simple" or "complex")
        """
        # Simple heuristic for Phase 1
        # In a real implementation, this would be more sophisticated
        
        words = query.split()
        
        if len(words) > 15 or len(entities) > 2:
            return "complex"
        else:
            return "simple" 