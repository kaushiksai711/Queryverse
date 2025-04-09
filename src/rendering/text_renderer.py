"""
Text Renderer for formatting text responses.

This module provides functionality for rendering responses
in text format with appropriate formatting and attribution.
"""

class TextRenderer:
    """
    Renderer for text-based responses.
    
    Responsibilities:
    - Format text responses from retrieval results
    - Add source attribution to responses
    - Handle different text formats (plain text, markdown)
    - Format confidence information when needed
    """
    
    def __init__(self):
        """
        Initialize the text renderer.
        """
        pass
    
    def render(self, results, context=None):
        """
        Render retrieval results as a text response.
        
        Args:
            results: Dictionary containing retrieval results and metadata
            context: Optional context information
            
        Returns:
            Formatted text response
        """
        # Default empty context if none provided
        if context is None:
            context = {}
        
        # Extract results data
        retrieved_items = results.get('results', [])
        confidence = results.get('confidence', 0)
        sources = results.get('sources', [])
        query = results.get('query', {})
        
        # If no results, return a default message
        if not retrieved_items:
            return "I'm sorry, I couldn't find any information on that topic."
        
        # Generate the main response text
        response_text = self._generate_response_text(retrieved_items, query)
        
        # Add source attribution if available
        if sources:
            response_text += self._format_sources(sources)
        
        # Add confidence statement for low confidence results
        if confidence < 0.7:
            response_text += "\n\nNote: I'm not entirely confident in this answer. You may want to verify this information."
        
        return response_text
    
    def _generate_response_text(self, retrieved_items, query):
        """
        Generate the main response text from retrieved items.
        
        Args:
            retrieved_items: List of retrieval results
            query: Original query information
            
        Returns:
            Generated response text
        """
        # For Phase 1, we'll use a simple approach that combines the top results
        
        # Get the top result
        top_result = retrieved_items[0] if retrieved_items else None
        
        if not top_result:
            return "I'm sorry, I couldn't find any specific information on that topic."
        
        # Use the text from the top result as the main response
        response = top_result.get('text', '')
        
        # If we have more results, add supplementary information
        if len(retrieved_items) > 1:
            # Add information from the second result if it's different enough
            second_result = retrieved_items[1]
            second_text = second_result.get('text', '')
            
            # Only add if it provides new information (simple check for Phase 1)
            if second_text and len(second_text) > 20 and second_text != response:
                response += "\n\nAdditionally: " + second_text
        
        return response
    
    def _format_sources(self, sources):
        """
        Format source attributions.
        
        Args:
            sources: List of source information
            
        Returns:
            Formatted source attribution text
        """
        if not sources:
            return ""
        
        # Format sources for Phase 1 (simple list)
        source_text = "\n\nSources:"
        for source in sources:
            source_text += f"\n- {source}"
        
        return source_text 