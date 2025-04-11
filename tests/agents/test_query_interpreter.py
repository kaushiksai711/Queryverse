import pytest
from src.agents.query_interpreter import QueryInterpreter

class TestQueryInterpreter:
    @pytest.fixture
    def interpreter(self):
        """Create a QueryInterpreter instance"""
        return QueryInterpreter()

    def test_interpret_basic(self, interpreter):
        """Test basic query interpretation"""
        # Test factual query
        result = interpreter.interpret("What are the symptoms of diabetes?")
        assert result["intent"] == "symptoms"
        assert "diabetes" in result["entities"]
        assert result["query_type"] == "factual"

        # Test causal query
        result = interpreter.interpret("What causes fever because of infection?")
        assert result["intent"] == "diagnosis"
        assert "fever" in result["entities"]
        assert "infection" in result["entities"]
        assert result["query_type"] == "causal"

        # Test comparative query
        result = interpreter.interpret("Compare symptoms of flu vs cold")
        assert result["intent"] == "symptoms"
        assert "flu" in result["entities"]
        assert "cold" in result["entities"]
        assert result["query_type"] == "comparative"

        # Test temporal query
        result = interpreter.interpret("When do symptoms of COVID-19 appear?")
        assert result["intent"] == "information"
        assert "COVID-19" in result["entities"]
        assert result["query_type"] == "temporal"

    def test_interpret_intents(self, interpreter):
        """Test different query intents"""
        # Test symptoms intent
        result = interpreter.interpret("What are the signs of pneumonia?")
        assert result["intent"] == "symptoms"

        # Test diagnosis intent
        result = interpreter.interpret("Why do I have a headache?")
        assert result["intent"] == "diagnosis"

        # Test treatment intent
        result = interpreter.interpret("How is malaria treated?")
        assert result["intent"] == "treatment"

        # Test prevention intent
        result = interpreter.interpret("How to prevent heart disease?")
        assert result["intent"] == "prevention"

        # Test information intent
        result = interpreter.interpret("What is hypertension?")
        assert result["intent"] == "information"

    def test_interpret_entities(self, interpreter):
        """Test entity extraction"""
        # Test medical conditions
        result = interpreter.interpret("What are the symptoms of asthma and bronchitis?")
        assert "asthma" in result["entities"]
        assert "bronchitis" in result["entities"]

        # Test symptoms
        result = interpreter.interpret("What causes fever and cough?")
        assert "fever" in result["entities"]
        assert "cough" in result["entities"]

        # Test treatments
        result = interpreter.interpret("What are the side effects of aspirin?")
        assert "aspirin" in result["entities"]

    def test_interpret_error_handling(self, interpreter):
        """Test error handling in query interpretation"""
        # Test empty query
        result = interpreter.interpret("")
        assert "error" in result

        # Test invalid query type
        result = interpreter.interpret(None)
        assert "error" in result

    def test_interpret_complex_queries(self, interpreter):
        """Test complex query interpretation"""
        # Test multi-part query
        result = interpreter.interpret("What are the symptoms and treatments for diabetes?")
        assert result["intent"] in ["symptoms", "treatment"]
        assert "diabetes" in result["entities"]

        # Test query with multiple conditions
        result = interpreter.interpret("Compare symptoms of flu and cold when caused by different viruses")
        assert result["query_type"] == "comparative"
        assert "flu" in result["entities"]
        assert "cold" in result["entities"]
        assert "viruses" in result["entities"] 