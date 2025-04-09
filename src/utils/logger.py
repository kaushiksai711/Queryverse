"""
Logging utility for the FAQ Chatbot system.

This module provides a consistent logging setup across
all components of the system.
"""

import logging
import os
import sys
from typing import Optional

def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Optional log level to override the default
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    log_level_str = os.environ.get("CHATBOT_LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Allow explicit override
    if level is not None:
        log_level = level
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Only add handler if not already present
    if not logger.handlers:
        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        
        # Set format
        log_format = os.environ.get(
            "CHATBOT_LOG_FORMAT", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
    
    return logger 