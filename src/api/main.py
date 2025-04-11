"""
Main API server for the medical chatbot.

This module provides the FastAPI application and routes
for the medical chatbot API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.agents.query_interpreter import QueryInterpreter
from src.agents.query_decomposer import QueryDecomposer
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.orchestrator import Orchestrator
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector
from src.db.mongodb_connector import MongoDBConnector
from src.rendering.text_renderer import TextRenderer
from src.utils.config import Config
from src.utils.logger import setup_logger

# Initialize components
config = Config()
logger = setup_logger("api")

# Initialize database connectors
neo4j = Neo4jConnector(
    uri=config.neo4j_uri,
    user=config.neo4j_user,
    password=config.neo4j_password
)

qdrant = QdrantConnector(
    url=config.qdrant_url,
    api_key=config.qdrant_api_key
)

mongodb = MongoDBConnector(
    uri=config.mongodb_uri,
    db_name=config.mongodb_db
)

# Initialize agents
query_interpreter = QueryInterpreter()
query_decomposer = QueryDecomposer(query_interpreter)
retrieval_agent = RetrievalAgent(neo4j, qdrant, mongodb)
orchestrator = Orchestrator(query_interpreter, query_decomposer, retrieval_agent)
text_renderer = TextRenderer()

# Create FastAPI app
app = FastAPI(
    title="Medical Chatbot API",
    description="API for the medical chatbot system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ChatRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    sources: list[str]
    status: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat query and return a response.
    
    Args:
        request: Chat request containing query and optional context
        
    Returns:
        Chat response with formatted text and sources
    """
    try:
        # Process the query through the orchestrator
        result = await orchestrator.process(request.query, request.context)
        
        # Format the response
        formatted_response = text_renderer.format_response(result)
        
        return ChatResponse(
            response=formatted_response,
            sources=result.get("sources", []),
            status=result.get("status", "success")
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status of the API and connected services
    """
    return {
        "status": "healthy",
        "services": {
            "neo4j": neo4j.is_connected(),
            "qdrant": qdrant.is_connected(),
            "mongodb": mongodb.is_connected()
        }
    } 