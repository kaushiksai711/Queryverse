import pytest
from unittest.mock import AsyncMock, MagicMock
from src.agents.query_decomposer import QueryDecomposer
from src.agents.query_interpreter import QueryInterpreter

class TestQueryDecomposer:
    @pytest.fixture
    def decomposer(self):
        interpreter = MagicMock(spec=QueryInterpreter)
        interpreter.interpret = AsyncMock(return_value={
            "query_type": "factual",
            "entities": ["diabetes"],
            "intent": "information"
        })
        return QueryDecomposer(interpreter)

    @pytest.mark.asyncio
    async def test_decompose_comparative(self, decomposer):
        """Test decomposition of comparative queries"""
        # Mock interpreter for this specific test
        decomposer.interpreter.interpret = AsyncMock(return_value={
            "query_type": "comparative",
            "entities": ["flu", "cold"],
            "intent": "comparison"
        })
        
        # Test simple comparison
        result = await decomposer.decompose("Compare symptoms of flu vs cold")
        assert result["is_complex"] is True
        assert len(result["sub_questions"]) > 1
        assert any("flu" in q for q in result["sub_questions"])
        assert any("cold" in q for q in result["sub_questions"])

    @pytest.mark.asyncio
    async def test_decompose_causal(self, decomposer):
        """Test decomposition of causal queries"""
        # Mock interpreter for causal query
        decomposer.interpreter.interpret = AsyncMock(return_value={
            "query_type": "causal",
            "entities": ["fever", "infection"],
            "intent": "cause"
        })
        
        # Test simple causal query
        result = await decomposer.decompose("What causes fever because of infection?")
        assert result["is_complex"] is True
        assert len(result["sub_questions"]) > 1
        assert "What causes fever?" in result["sub_questions"]
        assert "What is the relationship between fever and infection?" in result["sub_questions"]

    @pytest.mark.asyncio
    async def test_decompose_temporal(self, decomposer):
        """Test decomposition of temporal queries"""
        # Mock interpreter for temporal query
        decomposer.interpreter.interpret = AsyncMock(return_value={
            "query_type": "temporal",
            "entities": ["COVID-19"],
            "intent": "timeline"
        })
        
        # Test simple temporal query
        result = await decomposer.decompose("When do symptoms of COVID-19 appear?")
        assert result["is_complex"] is True
        assert len(result["sub_questions"]) > 1
        assert any("symptoms of COVID-19" in q for q in result["sub_questions"])
        assert any("timeline" in q for q in result["sub_questions"])

    @pytest.mark.asyncio
    async def test_decompose_simple(self, decomposer):
        """Test decomposition of simple queries"""
        # Mock interpreter for simple query
        decomposer.interpreter.interpret = AsyncMock(return_value={
            "query_type": "factual",
            "entities": ["diabetes"],
            "intent": "information"
        })
        
        # Test simple factual query
        result = await decomposer.decompose("What are the symptoms of diabetes?")
        assert result["is_complex"] is False
        assert len(result["sub_questions"]) == 1
        assert result["sub_questions"][0] == "What are the symptoms of diabetes?"

    @pytest.mark.asyncio
    async def test_decompose_error_handling(self, decomposer):
        """Test error handling in query decomposition"""
        # Test empty query
        result = await decomposer.decompose("")
        assert result["is_complex"] is False
        assert len(result["sub_questions"]) == 0
        
        # Test None query
        result = await decomposer.decompose(None)
        assert result["is_complex"] is False
        assert len(result["sub_questions"]) == 0

    @pytest.mark.asyncio
    async def test_decompose_multi_part(self, decomposer):
        """Test decomposition of multi-part queries"""
        # Mock interpreter for multi-part query
        decomposer.interpreter.interpret = AsyncMock(return_value={
            "query_type": "factual",
            "entities": ["pneumonia"],
            "intent": "information"
        })
        
        # Test query with multiple aspects
        result = await decomposer.decompose("What are the symptoms, causes, and treatments of pneumonia?")
        assert result["is_complex"] is True
        assert len(result["sub_questions"]) >= 3
        assert any("symptoms" in q for q in result["sub_questions"])
        assert any("causes" in q for q in result["sub_questions"])
        assert any("treatments" in q for q in result["sub_questions"]) 