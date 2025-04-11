"""
Configuration manager for the application.

This module provides functionality for loading and managing
configuration settings from environment variables and config files.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv
from src.utils.logger import setup_logger

logger = setup_logger("config")

class Config:
    """
    Manages application configuration.
    
    Responsibilities:
    - Load environment variables
    - Provide default values
    - Validate configuration
    - Access configuration values
    """
    
    def __init__(self):
        """Initialize the configuration manager"""
        # Load environment variables from .env file
        load_dotenv()
        
        # Database configuration
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password = os.getenv("NEO4J_PASSWORD", "password")
        
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.mongodb_db = os.getenv("MONGODB_DB", "medical_chatbot")
        
        # API configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # Model configuration
        self.model_name = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        
        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid
        """
        # Check required environment variables
        required_vars = [
            "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD",
            "QDRANT_URL",
            "MONGODB_URI", "MONGODB_DB"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.warning(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "neo4j": {
                "uri": self.neo4j_uri,
                "user": self.neo4j_user,
                "password": self.neo4j_password
            },
            "qdrant": {
                "url": self.qdrant_url,
                "api_key": self.qdrant_api_key
            },
            "mongodb": {
                "uri": self.mongodb_uri,
                "db_name": self.mongodb_db
            }
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration"""
        return {
            "host": self.api_host,
            "port": self.api_port
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration"""
        return {
            "name": self.model_name
        } 