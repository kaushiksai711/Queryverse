"""
Main application entry point with mock components for demonstration.
This serves as the entry point for the Phase 1 demo of the FAQ Chatbot system.
"""

from src.agents.orchestrator import Orchestrator
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.query_interpreter import QueryInterpreter
from src.knowledge.graph_manager import GraphManager
from src.knowledge.embedding_service import EmbeddingService
from src.rendering.text_renderer import TextRenderer
import logging
from src.utils.logger import setup_logger
from src.utils.config import load_config

# Setup logging
logger = setup_logger(__name__)

def main():
    """
    Main function to demonstrate the basic functionality of the FAQ Chatbot.
    """
    logger.info("Starting FAQ Chatbot Demo")
    
    # Load configuration
    config = load_config()
    
    # Initialize components with mock implementations
    graph_manager = GraphManager()
    embedding_service = EmbeddingService()
    
    # Initialize agents
    query_interpreter = QueryInterpreter()
    retrieval_agent = RetrievalAgent(graph_manager, embedding_service)
    
    # Initialize renderers
    text_renderer = TextRenderer()
    
    # Initialize orchestrator
    orchestrator = Orchestrator(
        query_interpreter=query_interpreter,
        retrieval_agent=retrieval_agent,
        text_renderer=text_renderer
    )
    
    # Demo queries
    demo_queries = [
        "What is a knowledge graph?",
        "How does semantic search work?",
        "What are the benefits of vector embeddings?",
    ]
    
    # Process demo queries
    for query in demo_queries:
        logger.info(f"Processing query: {query}")
        response = orchestrator.process_query(query)
        print(f"\nQ: {query}")
        print(f"A: {response}\n")
    
    logger.info("Demo completed")

if __name__ == "__main__":
    main() 