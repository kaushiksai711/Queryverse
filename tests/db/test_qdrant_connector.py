import pytest
from src.db.qdrant_connector import QdrantConnector
from sentence_transformers import SentenceTransformer
import os

@pytest.fixture
def qdrant_connector():
    """Fixture to create and connect a Qdrant connector"""
    connector = QdrantConnector()
    assert connector.connect(), "Failed to connect to Qdrant"
    yield connector
    connector.close()

@pytest.fixture
def model():
    """Fixture to create a sentence transformer model"""
    return SentenceTransformer('all-MiniLM-L6-v2')

def test_connection(qdrant_connector):
    """Test if Qdrant connection is established"""
    assert qdrant_connector.is_connected(), "Qdrant connector should be connected"

def test_search_functionality(qdrant_connector, model):
    """Test if Qdrant search is working correctly"""
    # Create a test query
    test_query = "What are the symptoms of high blood pressure?"
    
    # Generate embedding for the query
    query_vector = model.encode(test_query).tolist()
    
    # Perform search
    results = qdrant_connector.search(
        query_vector=query_vector,
        limit=3,
        score_threshold=0.7
    )
    
    # Verify results
    assert isinstance(results, list), "Results should be a list"
    if results:  # If we have results
        for result in results:
            assert 'id' in result, "Result should have an id"
            assert 'score' in result, "Result should have a score"
            assert 'payload' in result, "Result should have a payload"
            assert isinstance(result['score'], float), "Score should be a float"
            assert 0 <= result['score'] <= 1, "Score should be between 0 and 1"

def test_add_and_search_points(qdrant_connector, model):
    """Test adding points and searching for them"""
    # Create test points
    test_points = [
        {
            "id": "test_point_1",
            "vector": model.encode("High blood pressure symptoms include headaches and dizziness").tolist(),
            "payload": {
                "content": "High blood pressure symptoms include headaches and dizziness",
                "type": "symptom",
                "disease": "hypertension"
            }
        },
        {
            "id": "test_point_2",
            "vector": model.encode("Blood pressure medications help control hypertension").tolist(),
            "payload": {
                "content": "Blood pressure medications help control hypertension",
                "type": "treatment",
                "disease": "hypertension"
            }
        }
    ]
    
    # Add points
    qdrant_connector.add_points(test_points)
    
    # Search for the points
    query_vector = model.encode("blood pressure symptoms").tolist()
    results = qdrant_connector.search(
        query_vector=query_vector,
        limit=2,
        score_threshold=0.7
    )
    
    # Verify we found our test points
    found_ids = {result['id'] for result in results}
    assert "test_point_1" in found_ids, "Should find test_point_1"
    
    # Clean up
    qdrant_connector.delete_points(["test_point_1", "test_point_2"])

def test_delete_points(qdrant_connector, model):
    """Test deleting points from Qdrant"""
    # Add a test point
    test_point = {
        "id": "test_point_delete",
        "vector": model.encode("Test point for deletion").tolist(),
        "payload": {"content": "Test point for deletion"}
    }
    qdrant_connector.add_points([test_point])
    
    # Delete the point
    qdrant_connector.delete_points(["test_point_delete"])
    
    # Verify point is deleted
    query_vector = model.encode("Test point for deletion").tolist()
    results = qdrant_connector.search(
        query_vector=query_vector,
        limit=1,
        score_threshold=0.7
    )
    assert len(results) == 0, "Deleted point should not be found in search results" 