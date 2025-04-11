"""
Main API server for the FAQ Chatbot system.

This module sets up the FastAPI server for the chatbot system,
providing endpoints for chat interactions and feedback.
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from src.utils.logger import setup_logger
from src.utils.config import load_config
from src.agents.orchestrator import Orchestrator
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.query_interpreter import QueryInterpreter
from src.knowledge.graph_manager import GraphManager
from src.knowledge.embedding_service import EmbeddingService
from src.rendering.text_renderer import TextRenderer

# Setup logger
logger = setup_logger(__name__)

# Initialize app
app = FastAPI(
    title="FAQ Chatbot API",
    description="API for the FAQ Chatbot with Knowledge Retrieval",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
config = None
orchestrator = None

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global config, orchestrator
    logger.info("Starting up the API server")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize components
        graph_manager = GraphManager()
        embedding_service = EmbeddingService()
        query_interpreter = QueryInterpreter()
        retrieval_agent = RetrievalAgent(graph_manager, embedding_service)
        text_renderer = TextRenderer()
        
        # Initialize orchestrator
        orchestrator = Orchestrator(
            query_interpreter=query_interpreter,
            retrieval_agent=retrieval_agent,
            text_renderer=text_renderer
        )
        
        logger.info("Components initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down the API server")
    # Any cleanup code would go here

@app.get("/")
async def root():
    """Root endpoint providing basic information."""
    return {
        "message": "FAQ Chatbot API is running",
        "version": "0.1.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Import and include routers
from src.api.chat_routes import router as chat_router

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])

if __name__ == "__main__":
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True) 