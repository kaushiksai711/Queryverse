"""
Chat routes for the FAQ Chatbot API.

This module provides the API endpoints for chat interactions
with the FAQ chatbot system.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)

# -- Models for API interaction -- #

class ChatMessage(BaseModel):
    """Model for chat message requests."""
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Model for chat message responses."""
    response: str
    confidence: float
    sources: List[str] = []
    metadata: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    """Model for user feedback requests."""
    query_id: str
    helpful: bool
    corrections: Optional[Dict[str, Any]] = None
    additional_info: Optional[str] = None

# -- API endpoints -- #

@router.post("/query", response_model=ChatResponse)
async def process_query(message: ChatMessage, request: Request, background_tasks: BackgroundTasks):
    """
    Process a user query and return a response.
    
    Args:
        message: User query and context
        request: Request information
        background_tasks: Background task manager
        
    Returns:
        Response with answer and metadata
    """
    try:
        # Log the incoming query
        logger.info(f"Received query: {message.query}")
        
        # Get the orchestrator from the main app
        orchestrator = request.app.state.orchestrator
        if not orchestrator:
            # Get it from the main app object directly
            from api.main import orchestrator
            if not orchestrator:
                raise HTTPException(status_code=500, detail="Orchestrator not initialized")
        
        # Process the query
        context = message.context or {}
        response = orchestrator.process_query(message.query, context)
        
        # For Phase 1, we'll just use a mock response if the orchestrator fails
        if not response:
            mock_response = "This is a mock response for Phase 1. In the full implementation, this would be a comprehensive answer from the knowledge base."
            return ChatResponse(
                response=mock_response,
                confidence=0.7,
                sources=["Mock Knowledge Base"],
                metadata={"query_id": "mock_id_123"}
            )
        
        # Assume the orchestrator returns a string for Phase 1
        # In Phase 2, it would return a structured result with confidence, sources, etc.
        if isinstance(response, str):
            # Mock confidence and sources for Phase 1
            return ChatResponse(
                response=response,
                confidence=0.8,
                sources=["Internal Knowledge Base"],
                metadata={"query_id": "generated_id_123"}
            )
        else:
            # If orchestrator returns a structured result
            return ChatResponse(
                response=response.get("text", "No response generated"),
                confidence=response.get("confidence", 0.5),
                sources=response.get("sources", []),
                metadata=response.get("metadata", {})
            )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Submit feedback about a previous response.
    
    Args:
        feedback: User feedback information
        request: Request information
        background_tasks: Background task manager
    
    Returns:
        Acknowledgement of feedback receipt
    """
    try:
        # Log the feedback
        logger.info(f"Received feedback for query {feedback.query_id}: helpful={feedback.helpful}")
        
        # In Phase 1, we'll just log the feedback
        # In Phase 2, this would update the knowledge base
        
        # Schedule background task to process feedback in Phase 2
        # background_tasks.add_task(process_feedback, feedback)
        
        return {"status": "success", "message": "Feedback received, thank you!"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing feedback: {str(e)}")

@router.get("/history/{user_id}")
async def get_chat_history(user_id: str, request: Request, limit: int = 10):
    """
    Get chat history for a user.
    
    Args:
        user_id: User identifier
        request: Request information
        limit: Maximum number of history items to return
        
    Returns:
        List of chat interactions
    """
    try:
        # For Phase 1, return mock history
        mock_history = [
            {
                "query": "What is a knowledge graph?",
                "response": "A knowledge graph is a network-based representation of knowledge that uses nodes to represent entities and edges to represent relationships between entities.",
                "timestamp": "2023-10-15T14:25:30Z"
            },
            {
                "query": "How does semantic search work?",
                "response": "Semantic search is a search technique that understands the contextual meaning of terms to improve accuracy of search results beyond keyword matching.",
                "timestamp": "2023-10-15T14:27:45Z"
            }
        ]
        
        return {
            "user_id": user_id,
            "history": mock_history[:limit],
            "total_interactions": len(mock_history)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}") 