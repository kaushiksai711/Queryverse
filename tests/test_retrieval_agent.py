import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.retrieval_agent import RetrievalAgent
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector
from src.db.mongodb_connector import MongoDBConnector

class TestRetrievalAgent:
    @pytest.fixture
    def agent(self):
        """Create a RetrievalAgent instance with mocked dependencies"""
        # Mock the database connectors
        vector_db = MagicMock(spec=QdrantConnector)
        graph_db = MagicMock(spec=Neo4jConnector)
        mongodb = MagicMock(spec=MongoDBConnector)
        
        # Mock connection status
        vector_db.is_connected = MagicMock(return_value=True)
        graph_db.is_connected = MagicMock(return_value=True)
        mongodb.is_connected = MagicMock(return_value=True)
        
        # Mock MongoDB search
        mongodb.search = AsyncMock(return_value=[
            {"content": "Diabetes treatment includes insulin therapy", "score": 0.9}
        ])
        
        # Mock vector search
        vector_db.search = AsyncMock(return_value=[
            {"content": "Diabetes treatment includes insulin therapy", "score": 0.9},
            {"content": "Type 2 Diabetes can be treated with metformin", "score": 0.8}
        ])
        
        # Mock graph search
        graph_db.execute_query = AsyncMock(return_value=[
            {
                "disease": "Type 2 Diabetes",
                "description": "A chronic condition affecting blood sugar levels",
                "treatments": [
                    {"name": "Metformin", "description": "First-line medication for Type 2 Diabetes"},
                    {"name": "Insulin", "description": "Hormone therapy for blood sugar control"}
                ]
            }
        ])
        
        return RetrievalAgent(vector_db, graph_db, mongodb)

    @pytest.mark.asyncio
    async def test_retrieve(self, agent):
        """Test retrieval of information"""
        # Test with a treatment query
        query = "What are the treatments for Type 2 Diabetes?"
        result = await agent.retrieve(query)
        
        # Check response structure
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "success"
        
        # Check knowledge data
        knowledge = result.get("knowledge", [])
        assert len(knowledge) > 0
        
        first_result = knowledge[0]
        assert "Type 2 Diabetes" in first_result.get("disease", "")
        assert len(first_result.get("treatments", [])) > 0
        
        # Test error handling
        agent.vector_db.search = AsyncMock(side_effect=Exception("Test error"))
        error_result = await agent.retrieve("test query")
        assert error_result["status"] == "error"

@pytest.fixture
def mocked_retrieval_agent():
    """Create a retrieval agent with mocked dependencies for integration tests"""
    vector_db = MagicMock(spec=QdrantConnector)
    graph_db = MagicMock(spec=Neo4jConnector)
    mongodb = MagicMock(spec=MongoDBConnector)
    
    # Mock connection status
    vector_db.is_connected = MagicMock(return_value=True)
    graph_db.is_connected = MagicMock(return_value=True)
    mongodb.is_connected = MagicMock(return_value=True)
    
    # Mock MongoDB search
    mongodb.search = AsyncMock(return_value=[
        {"content": "Type 2 Diabetes treatment includes metformin", "score": 0.95}
    ])
    
    # Mock vector search results
    vector_db.search = AsyncMock(return_value=[
        {"content": "Type 2 Diabetes treatment includes metformin", "score": 0.95},
        {"content": "Insulin is used to treat diabetes", "score": 0.85}
    ])
    
    # Mock graph search results
    graph_db.execute_query = AsyncMock(return_value=[{
        "disease": "Type 2 Diabetes",
        "description": "A metabolic disorder characterized by high blood sugar",
        "treatments": [
            {"name": "Metformin", "description": "First-line medication"},
            {"name": "Insulin", "description": "Hormone therapy"}
        ]
    }])
    
    return RetrievalAgent(vector_db, graph_db, mongodb)

@pytest.mark.asyncio
async def test_treatment_query_relevance(mocked_retrieval_agent):
    """Test that treatment queries return only relevant results."""
    query = "What are the treatments for Type 2 Diabetes?"
    result = await mocked_retrieval_agent.retrieve(query)
    
    assert result["status"] == "success"
    knowledge = result.get("knowledge", [])
    
    if isinstance(knowledge, list) and knowledge:
        first_result = knowledge[0]
        assert "Type 2 Diabetes" in first_result.get("disease", "")
        treatments = first_result.get("treatments", [])
        assert len(treatments) > 0
        assert any("Metformin" in t.get("name", "") for t in treatments)

@pytest.mark.asyncio
async def test_query_exact_match_priority(mocked_retrieval_agent):
    """Test that exact matches are prioritized."""
    query = "What are the treatments for Type 2 Diabetes?"
    result = await mocked_retrieval_agent.retrieve(query)
    
    knowledge = result.get("knowledge", [])
    if isinstance(knowledge, list) and knowledge:
        first_result = knowledge[0]
        assert "Type 2 Diabetes" in first_result.get("disease", "")

@pytest.mark.asyncio
async def test_treatment_relationship_accuracy(mocked_retrieval_agent):
    """Test treatment relationships are correct."""
    query = "What medications are used to treat Type 2 Diabetes?"
    result = await mocked_retrieval_agent.retrieve(query)
    
    knowledge = result.get("knowledge", [])
    if isinstance(knowledge, list) and knowledge:
        first_result = knowledge[0]
        treatments = first_result.get("treatments", [])
        assert len(treatments) > 0
        for treatment in treatments:
            assert "name" in treatment
            assert "description" in treatment

def test_intent_detection(mocked_retrieval_agent):
    """Test query intent detection."""
    assert mocked_retrieval_agent._determine_intent("What are the treatments for diabetes?") == "treatment"
    assert mocked_retrieval_agent._determine_intent("How is diabetes treated?") == "treatment"
    assert mocked_retrieval_agent._determine_intent("What are the symptoms of diabetes?") == "symptoms" 