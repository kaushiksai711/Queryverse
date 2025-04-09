"""
Configuration loader utility.

This module provides functionality for loading and validating
configuration settings for the FAQ Chatbot system.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Default configuration
DEFAULT_CONFIG = {
    "api": {
        "host": "0.0.0.0",
        "port": 8000,
        "debug": True
    },
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "database": {
        "neo4j": {
            "uri": "mock://localhost:7687",
            "user": "neo4j",
            "password": "password"
        },
        "qdrant": {
            "url": "mock://localhost:6333",
            "collection_name": "knowledge"
        }
    },
    "retrieval": {
        "top_k": 5,
        "min_confidence": 0.5
    }
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a file or environment variables,
    falling back to default values if not specified.
    
    Args:
        config_path: Optional path to a JSON configuration file
        
    Returns:
        Configuration dictionary
    """
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from file if specified
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                # Update the default config with file values
                _update_nested_dict(config, file_config)
            logging.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logging.warning(f"Error loading config from {config_path}: {str(e)}")
    
    # Override with environment variables
    _override_from_env(config)
    
    return config

def _update_nested_dict(base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
    """
    Update a nested dictionary with values from another dictionary.
    
    Args:
        base_dict: Base dictionary to update
        update_dict: Dictionary with values to update
    """
    for key, value in update_dict.items():
        if (
            key in base_dict and 
            isinstance(base_dict[key], dict) and 
            isinstance(value, dict)
        ):
            _update_nested_dict(base_dict[key], value)
        else:
            base_dict[key] = value

def _override_from_env(config: Dict[str, Any], prefix: str = "CHATBOT_") -> None:
    """
    Override configuration values from environment variables.
    
    Environment variables should be in the format:
    CHATBOT_SECTION_SUBSECTION_KEY=value
    
    Args:
        config: Configuration dictionary to update
        prefix: Prefix for environment variables
    """
    for env_name, env_value in os.environ.items():
        if env_name.startswith(prefix):
            # Remove prefix and split into parts
            config_path = env_name[len(prefix):].lower().split('_')
            
            # Navigate to the correct level in the config
            current = config
            for part in config_path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value (convert to appropriate type if possible)
            key = config_path[-1]
            try:
                # Try to parse as JSON for complex types
                current[key] = json.loads(env_value)
            except json.JSONDecodeError:
                # If not valid JSON, use the string value
                current[key] = env_value 