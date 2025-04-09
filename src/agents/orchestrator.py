"""
Orchestrator module for coordinating workflow between agents.

This module contains the main orchestrator class that coordinates
the interaction between the query interpreter, retrieval agent,
and renderer components.
"""

class Orchestrator:
    """
    Orchestrator class for coordinating the workflow between different agents.
    
    Responsibilities:
    - Coordinate the workflow between query interpreter and retrieval agent
    - Manage the processing pipeline for user queries
    - Control the flow of information between components
    - Deliver final responses using appropriate renderers
    """
    
    def __init__(self, query_interpreter, retrieval_agent, text_renderer):
        """
        Initialize the orchestrator with required components.
        
        Args:
            query_interpreter: Component for understanding user queries
            retrieval_agent: Component for retrieving information
            text_renderer: Component for rendering text responses
        """
        self.query_interpreter = query_interpreter
        self.retrieval_agent = retrieval_agent
        self.text_renderer = text_renderer
    
    def process_query(self, query, context=None):
        """
        Process a user query and return a response.
        
        Args:
            query: User's question or request as a string
            context: Optional context information (e.g., user ID, preferences)
            
        Returns:
            Formatted response as a string
        """
        # Default empty context if none provided
        if context is None:
            context = {}
        
        # Interpret the query
        interpreted_query = self.query_interpreter.interpret(query, context)
        
        # Retrieve information
        retrieval_results = self.retrieval_agent.retrieve(interpreted_query, context)
        
        # Check if we have sufficient information
        if retrieval_results.get('confidence', 0) < 0.5:
            # For Phase 1, we'll just acknowledge insufficient information
            return "I'm sorry, I don't have enough information to answer that question confidently."
        
        # Render the response
        response = self.text_renderer.render(retrieval_results, context)
        
        return response 