import os
from dotenv import load_dotenv
import pytest
from src.agents.query_interpreter import QueryInterpreter
from src.agents.query_decomposer import QueryDecomposer
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.orchestrator import Orchestrator
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector
from src.db.mongodb_connector import MongoDBConnector
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

@pytest.fixture
def setup_components():
    """Set up all required components for testing"""
    # Initialize database connectors
    neo4j = Neo4jConnector(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    
    qdrant = QdrantConnector(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    mongodb = MongoDBConnector(
        uri=os.getenv("MONGODB_URI"),
        db_name=os.getenv("MONGODB_DB")
    )
    
    # Connect to databases
    neo4j.connect()
    qdrant.connect()
    mongodb.connect()
    
    # Initialize agents
    query_interpreter = QueryInterpreter()
    query_decomposer = QueryDecomposer(query_interpreter)
    retrieval_agent = RetrievalAgent(neo4j, qdrant, mongodb)
    orchestrator = Orchestrator(query_interpreter, query_decomposer, retrieval_agent)
    
    # Yield the components
    yield {
        "neo4j": neo4j,
        "qdrant": qdrant,
        "mongodb": mongodb,
        "query_interpreter": query_interpreter,
        "query_decomposer": query_decomposer,
        "retrieval_agent": retrieval_agent,
        "orchestrator": orchestrator
    }
    
    # Clean up: disconnect from databases
    neo4j.disconnect()
    qdrant.disconnect()
    mongodb.disconnect()

@pytest.mark.asyncio
async def test_query_interpreter(setup_components):
    """Test the query interpreter"""
    interpreter = setup_components["query_interpreter"]
    
    # Test simple query
    result = await interpreter.interpret("What are the symptoms of diabetes?")
    assert "query_type" in result
    assert "entities" in result
    assert "intent" in result

@pytest.mark.asyncio
async def test_query_decomposer(setup_components):
    """Test the query decomposer"""
    decomposer = setup_components["query_decomposer"]
    
    # Test simple query
    result = await decomposer.decompose("What are the symptoms of diabetes?")
    assert "is_complex" in result
    assert "sub_questions" in result
    assert "original_query" in result

@pytest.mark.asyncio
async def test_retrieval_agent(setup_components):
    """Test the retrieval agent"""
    agent = setup_components["retrieval_agent"]
    
    # Test simple retrieval
    result = await agent.retrieve("What are the symptoms of diabetes?")
    assert isinstance(result, dict)
    assert "knowledge" in result
    assert "sources" in result

@pytest.mark.asyncio
async def test_orchestrator(setup_components):
    """Test the orchestrator"""
    orchestrator = setup_components["orchestrator"]
    
    # Test simple orchestration
    result = await orchestrator.process_query("What are the symptoms of diabetes?")
    assert isinstance(result, dict)
    assert "response" in result
    assert "sources" in result

@pytest.mark.asyncio
async def test_end_to_end(setup_components):
    """Test the end-to-end workflow"""
    orchestrator = setup_components["orchestrator"]
    
    # Test complex query
    result = await orchestrator.process_query("Compare symptoms of flu vs cold")
    assert isinstance(result, dict)
    assert "response" in result
    assert "sources" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 