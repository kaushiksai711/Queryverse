"""
Tests for the orchestrator component.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.agents.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    """Test cases for the Orchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock components
        self.mock_query_interpreter = MagicMock()
        self.mock_retrieval_agent = MagicMock()
        self.mock_text_renderer = MagicMock()
        
        # Create orchestrator with mock components
        self.orchestrator = Orchestrator(
            query_interpreter=self.mock_query_interpreter,
            retrieval_agent=self.mock_retrieval_agent,
            text_renderer=self.mock_text_renderer
        )
    
    def test_process_query_happy_path(self):
        """Test the basic happy path for query processing."""
        # Configure mocks
        self.mock_query_interpreter.interpret.return_value = {
            'text': 'test query',
            'entities': ['knowledge_graph'],
            'intent': {'type': 'definition', 'confidence': 0.8},
            'complexity': 'simple'
        }
        
        self.mock_retrieval_agent.retrieve.return_value = {
            'results': [{'text': 'Result text', 'source': 'Test Source'}],
            'confidence': 0.8,
            'sources': ['Test Source'],
            'query': {'text': 'test query'}
        }
        
        self.mock_text_renderer.render.return_value = "Formatted test response"
        
        # Call the method
        result = self.orchestrator.process_query("test query")
        
        # Verify interactions
        self.mock_query_interpreter.interpret.assert_called_once()
        self.mock_retrieval_agent.retrieve.assert_called_once()
        self.mock_text_renderer.render.assert_called_once()
        
        # Check the result
        self.assertEqual(result, "Formatted test response")
    
    def test_process_query_low_confidence(self):
        """Test handling of low confidence results."""
        # Configure mocks
        self.mock_query_interpreter.interpret.return_value = {
            'text': 'test query',
            'entities': [],
            'intent': {'type': 'unknown', 'confidence': 0.3},
            'complexity': 'simple'
        }
        
        self.mock_retrieval_agent.retrieve.return_value = {
            'results': [],
            'confidence': 0.2,  # Low confidence
            'sources': [],
            'query': {'text': 'test query'}
        }
        
        # Call the method
        result = self.orchestrator.process_query("test query")
        
        # Verify the renderer was not called (low confidence short-circuit)
        self.mock_text_renderer.render.assert_not_called()
        
        # Check the result is an apology message
        self.assertIn("I'm sorry", result)
        self.assertIn("don't have enough information", result)
    
    def test_process_query_with_context(self):
        """Test query processing with context information."""
        # Create a mock context
        context = {"user_id": "test_user", "format_preferences": {"include_sources": True}}
        
        # Configure mocks
        self.mock_query_interpreter.interpret.return_value = {
            'text': 'test query',
            'entities': ['vector_embeddings'],
            'intent': {'type': 'explanation', 'confidence': 0.9},
            'complexity': 'simple'
        }
        
        self.mock_retrieval_agent.retrieve.return_value = {
            'results': [{'text': 'Vector embeddings explanation', 'source': 'Knowledge Base'}],
            'confidence': 0.9,
            'sources': ['Knowledge Base'],
            'query': {'text': 'test query'}
        }
        
        self.mock_text_renderer.render.return_value = "Formatted explanation with sources"
        
        # Call the method with context
        result = self.orchestrator.process_query("test query", context)
        
        # Verify context was passed to components
        self.mock_query_interpreter.interpret.assert_called_with("test query", context)
        
        # Check the result
        self.assertEqual(result, "Formatted explanation with sources")

if __name__ == "__main__":
    unittest.main() 