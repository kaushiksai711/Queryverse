"""
Text renderer for formatting responses.

This module provides functionality for formatting text responses
in a consistent and readable way.
"""

from typing import Dict, Any, List
from src.utils.logger import setup_logger

logger = setup_logger("text_renderer")

class TextRenderer:
    """
    Renders text responses in a consistent format.
    
    Responsibilities:
    - Format success responses
    - Format error responses
    - Format no-results responses
    - Format knowledge base responses
    """
    
    def __init__(self):
        """Initialize the text renderer"""
        self.logger = logger
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """
        Format a response into a readable text format.
        
        Args:
            response: Response dictionary from the retrieval agent
            
        Returns:
            Formatted text response
        """
        if response.get("status") == "error":
            return self._format_error(response)
        
        if not response.get("knowledge"):
            return self._format_no_results()
        
        if isinstance(response["knowledge"], str):
            return response["knowledge"]
        
        return self._format_knowledge(response["knowledge"])
    
    def _format_error(self, response: Dict[str, Any]) -> str:
        """Format an error response"""
        error_msg = response.get("error", "An unknown error occurred")
        return f"I'm sorry, I encountered an error: {error_msg}"
    
    def _format_no_results(self) -> str:
        """Format a no-results response"""
        return "I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or provide more details?"
    
    def _format_knowledge(self, knowledge: List[Dict[str, Any]]) -> str:
        """Format knowledge base results"""
        if not knowledge:
            return self._format_no_results()
        
        formatted_results = []
        for result in knowledge:
            source = result.get("source", "unknown")
            content = result.get("content", "")
            
            if source == "graph":
                formatted_results.append(f"From medical database: {content}")
            else:
                formatted_results.append(content)
        
        return "\n\n".join(formatted_results) 