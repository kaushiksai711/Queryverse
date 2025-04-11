"""
Tests for the chat API routes.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.api.main import app
from src.api.chat_routes import ChatMessage, ChatResponse, FeedbackRequest

class TestChatRoutes(unittest.TestCase):
    """Test cases for the chat API routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        
        # Create a mock orchestrator
        self.mock_orchestrator = MagicMock()
        
        # Patch the app state to use the mock orchestrator
        app.state.orchestrator = self.mock_orchestrator
    
    def test_process_query_endpoint(self):
        """Test the query processing endpoint."""
        # Configure mock orchestrator
        self.mock_orchestrator.process_query.return_value = "This is a test response"
        
        # Create a test query
        test_query = {
            "query": "What is a knowledge graph?",
            "context": {"user_id": "test_user"}
        }
        
        # Send a request to the endpoint
        response = self.client.post("/api/chat/query", json=test_query)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        self.assertIn("confidence", data)
        self.assertIn("sources", data)
        self.assertIn("metadata", data)
        
        # Verify the mock was called with the right parameters
        self.mock_orchestrator.process_query.assert_called_with(
            "What is a knowledge graph?", 
            {"user_id": "test_user"}
        )
    
    def test_process_query_endpoint_error(self):
        """Test error handling in the query processing endpoint."""
        # Configure mock orchestrator to raise an exception
        self.mock_orchestrator.process_query.side_effect = Exception("Test error")
        
        # Create a test query
        test_query = {
            "query": "What is a knowledge graph?",
            "context": {"user_id": "test_user"}
        }
        
        # Send a request to the endpoint
        response = self.client.post("/api/chat/query", json=test_query)
        
        # Check the response
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("detail", data)
        self.assertIn("Error processing query", data["detail"])
    
    def test_feedback_endpoint(self):
        """Test the feedback submission endpoint."""
        # Create a test feedback request
        test_feedback = {
            "query_id": "test_query_123",
            "helpful": True,
            "corrections": {"entity": "knowledge_graph", "update": "New definition"},
            "additional_info": "This is a test feedback"
        }
        
        # Send a request to the endpoint
        response = self.client.post("/api/chat/feedback", json=test_feedback)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Feedback received", data["message"])
    
    def test_history_endpoint(self):
        """Test the chat history endpoint."""
        # Define a test user ID
        test_user_id = "test_user_123"
        
        # Send a request to the endpoint
        response = self.client.get(f"/api/chat/history/{test_user_id}")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], test_user_id)
        self.assertIn("history", data)
        self.assertIsInstance(data["history"], list)
        self.assertIn("total_interactions", data)
    
    def test_history_endpoint_with_limit(self):
        """Test the chat history endpoint with a custom limit."""
        # Define a test user ID and limit
        test_user_id = "test_user_123"
        test_limit = 1
        
        # Send a request to the endpoint with limit parameter
        response = self.client.get(f"/api/chat/history/{test_user_id}?limit={test_limit}")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], test_user_id)
        self.assertIn("history", data)
        self.assertLessEqual(len(data["history"]), test_limit)

if __name__ == "__main__":
    unittest.main() 