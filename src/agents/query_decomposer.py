"""
Query Decomposer for breaking down complex queries into simpler sub-questions.

This module contains the implementation of the query decomposer
which is responsible for analyzing complex queries and breaking them
down into simpler sub-questions that can be answered individually.
"""

class QueryDecomposer:
    """
    Agent responsible for decomposing complex queries into simpler sub-questions.
    
    Responsibilities:
    - Identify if a query is complex enough to require decomposition
    - Break down complex queries into manageable sub-questions
    - Maintain relationships between sub-questions and original query
    - Prioritize sub-questions for efficient processing
    """
    
    def __init__(self):
        """
        Initialize the query decomposer.
        """
        pass
    
    def decompose(self, query, context=None):
        """
        Decompose a complex query into simpler sub-questions.
        
        Args:
            query: Interpreted query object from query interpreter
            context: Optional context information
            
        Returns:
            List of sub-questions if query is complex, otherwise returns the original query
        """
        # Default empty context if none provided
        if context is None:
            context = {}
        
        # Only decompose if query is complex
        if query.get('complexity') != 'complex':
            return [query]  # Return original query if not complex
        
        # Simplified mock implementation for Phase 1
        query_text = query.get('text', '')
        entities = query.get('entities', [])
        intent = query.get('intent', {})
        
        # Generate sub-questions based on simple patterns
        sub_questions = self._generate_sub_questions(query_text, entities, intent)
        
        # Prioritize sub-questions
        prioritized = self._prioritize_sub_questions(sub_questions)
        
        return prioritized
    
    def _generate_sub_questions(self, query_text, entities, intent):
        """
        Generate sub-questions from a complex query.
        
        Args:
            query_text: Original query text
            entities: Extracted entities from the query
            intent: Identified intent of the query
            
        Returns:
            List of sub-question objects
        """
        # Mock implementation for Phase 1
        # In a real implementation, this would use more sophisticated techniques
        
        sub_questions = []
        
        # Create a simple definition question for each entity
        for entity in entities:
            sub_q = {
                'text': f"What is {entity}?",
                'entities': [entity],
                'intent': {'type': 'definition', 'confidence': 0.9},
                'complexity': 'simple',
                'parent_query': query_text,
                'type': 'definition'
            }
            sub_questions.append(sub_q)
        
        # If it's a comparison intent, add relationship questions
        if intent.get('type') == 'comparison' and len(entities) >= 2:
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    sub_q = {
                        'text': f"What is the relationship between {entities[i]} and {entities[j]}?",
                        'entities': [entities[i], entities[j]],
                        'intent': {'type': 'relationship', 'confidence': 0.8},
                        'complexity': 'simple',
                        'parent_query': query_text,
                        'type': 'relationship'
                    }
                    sub_questions.append(sub_q)
        
        return sub_questions
    
    def _prioritize_sub_questions(self, sub_questions):
        """
        Prioritize sub-questions for efficient processing.
        
        Args:
            sub_questions: List of generated sub-questions
            
        Returns:
            Prioritized list of sub-questions
        """
        # Simple priority rules for Phase 1:
        # 1. Definition questions first (to establish basic understanding)
        # 2. Relationship questions next
        # 3. Other questions last
        
        definitions = []
        relationships = []
        others = []
        
        for q in sub_questions:
            q_type = q.get('type', '')
            if q_type == 'definition':
                definitions.append(q)
            elif q_type == 'relationship':
                relationships.append(q)
            else:
                others.append(q)
        
        # Combine in priority order
        return definitions + relationships + others 