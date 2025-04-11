import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.retrieval_agent import RetrievalAgent
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector

class TestRetrievalAgent:
    @pytest.fixture
    def agent(self):
        """Create a RetrievalAgent instance with mocked dependencies"""
        # Mock the database connectors
        vector_db = MagicMock(spec=QdrantConnector)
        graph_db = MagicMock(spec=Neo4jConnector)
        
        # Mock the search methods
        vector_db.search = AsyncMock(return_value=[
            {"content": "Flu symptoms include fever, cough, and fatigue", "score": 0.9},
            {"content": "Common cold symptoms are runny nose and sore throat", "score": 0.8}
        ])
        
        graph_db.search = AsyncMock(return_value=[
            {"content": "Flu is caused by influenza virus", "score": 0.85},
            {"content": "Cold is caused by rhinovirus", "score": 0.75}
        ])
        
        return RetrievalAgent(vector_db, graph_db)

    async def test_retrieve(self, agent):
        """Test retrieval of information"""
        # Test with a simple query
        query = "What are the symptoms of flu?"
        result = await agent.retrieve(query)
        
        # Check response structure
        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        assert "results" in result
        
        # Test with a complex query
        query = "Compare symptoms of flu vs cold"
        result = await agent.retrieve(query)
        assert isinstance(result, dict)
        assert "status" in result
        assert "message" in result
        assert "results" in result
        
        # Test with no results
        query = "What are the symptoms of a non-existent disease?"
        result = await agent.retrieve(query)
        assert result["status"] == "success"
        assert "I couldn't find specific information" in result["message"]
        assert result["results"] == []
        
        # Test error handling
        # Mock an error in vector_db.search
        agent.vector_db.search = AsyncMock(side_effect=Exception("Test error"))
        result = await agent.retrieve("test query")
        assert result["status"] == "error"
        assert "I encountered an error" in result["message"]
        assert result["results"] == [] 