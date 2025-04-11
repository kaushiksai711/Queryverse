"""
Query Decomposer for breaking down complex queries into simpler sub-questions.

This module contains the implementation of the query decomposer
which is responsible for breaking down complex queries into simpler
sub-questions that can be processed individually.
"""

from typing import Dict, Any, List
from src.utils.logger import setup_logger
import re

class QueryDecomposer:
    """
    Agent responsible for decomposing complex queries into simpler sub-questions.
    
    Responsibilities:
    - Identify complex queries that need decomposition
    - Break down queries into simpler sub-questions
    - Maintain context and relationships between sub-questions
    - Handle different types of complex queries (comparative, causal, temporal)
    """
    
    def __init__(self, query_interpreter):
        """
        Initialize the query decomposer with a query interpreter
        
        Args:
            query_interpreter: An instance of QueryInterpreter
        """
        self.interpreter = query_interpreter
        self.logger = setup_logger("query_decomposer")
    
    async def decompose(self, query: str) -> Dict[str, Any]:
        """Decompose a query into sub-questions if it's complex"""
        if not query or not query.strip():
            return {
                "is_complex": False,
                "sub_questions": [],
                "original_query": query
            }

        # Interpret the query first
        interpretation = await self.interpreter.interpret(query)
        
        # If it's a simple query with one entity and no complex aspects, return as is
        if (interpretation["query_type"] == "factual" and 
            len(interpretation["entities"]) == 1 and
            not any(word in query.lower() for word in ["vs", "compared", "because", "when", "how long"]) and
            len([word for word in ["symptoms", "causes", "treatments"] if word in query.lower()]) <= 1):
            return {
                "is_complex": False,
                "sub_questions": [query],
                "original_query": query
            }

        # Handle different query types
        sub_questions = []
        if interpretation["query_type"] == "comparative":
            sub_questions = self._decompose_comparative(query, interpretation["entities"])
        elif interpretation["query_type"] == "causal":
            sub_questions = self._decompose_causal(query, interpretation["entities"])
        elif interpretation["query_type"] == "temporal":
            sub_questions = self._decompose_temporal(query, interpretation["entities"])
        else:
            # Check for multi-part queries
            if (len(interpretation["entities"]) > 1 or
                any(word in query.lower() for word in ["vs", "compared"]) or
                len([word for word in ["symptoms", "causes", "treatments"] if word in query.lower()]) > 1):
                sub_questions = self._decompose_multi_part(query, interpretation["entities"])

        result = {
            "is_complex": len(sub_questions) > 1,
            "sub_questions": sub_questions if sub_questions else [query],
            "original_query": query
        }
        
        self.logger.info(f"Decomposed query: {result}")
        return result
    
    def _decompose_comparative(self, query: str, entities: List[str]) -> List[str]:
        """Decompose a comparative query into sub-questions"""
        sub_questions = []
        
        # Extract the aspects being compared (e.g., symptoms, treatments)
        aspects = []
        if "symptom" in query.lower():
            aspects.append("symptoms")
        if "treatment" in query.lower() or "treat" in query.lower():
            aspects.append("treatments")
        if "cause" in query.lower():
            aspects.append("causes")
        
        # If no specific aspects mentioned, default to symptoms
        if not aspects:
            aspects = ["symptoms"]
        
        # Use the entities directly if available
        if len(entities) >= 2:
            for aspect in aspects:
                for entity in entities:
                    if aspect == "symptoms":
                        sub_questions.append(f"What are the symptoms of {entity}?")
                    elif aspect == "treatments":
                        sub_questions.append(f"What are the treatments for {entity}?")
                    elif aspect == "causes":
                        sub_questions.append(f"What are the causes of {entity}?")
        else:
            # Clean the query by removing comparison words
            clean_query = re.sub(r'\b(compare|vs|versus)\b', '', query, flags=re.IGNORECASE)
            
            # Split the query into parts
            parts = re.split(r'\band\b', clean_query, flags=re.IGNORECASE)
            conditions = [part.strip() for part in parts if part.strip()]
            
            # Generate sub-questions for each aspect and condition
            for aspect in aspects:
                for condition in conditions:
                    # Extract the main entity from the condition
                    entity = self._extract_main_entity(condition)
                    if entity:
                        if aspect == "symptoms":
                            sub_questions.append(f"What are the symptoms of {entity}?")
                        elif aspect == "treatments":
                            sub_questions.append(f"What are the treatments for {entity}?")
                        elif aspect == "causes":
                            sub_questions.append(f"What are the causes of {entity}?")
        
        return sub_questions
    
    def _decompose_causal(self, query: str, entities: List[str]) -> List[str]:
        """Decompose causal queries into sub-questions"""
        sub_questions = []
        if len(entities) >= 2:
            effect = entities[0]
            cause = entities[1]
            sub_questions.append(f"What causes {effect}?")
            sub_questions.append(f"What is the relationship between {effect} and {cause}?")
        return sub_questions
    
    def _decompose_temporal(self, query: str, entities: List[str]) -> List[str]:
        """Decompose temporal queries into sub-questions"""
        sub_questions = []
        if entities:
            entity = entities[0]
            sub_questions.append(f"What are the symptoms of {entity}?")
            sub_questions.append(f"What is the timeline of {entity} symptoms?")
        return sub_questions
    
    def _decompose_multi_part(self, query: str, entities: List[str]) -> List[str]:
        """Decompose multi-part queries into sub-questions"""
        sub_questions = []
        if entities:
            entity = entities[0]
            # Check for multiple aspects in the query
            aspects = []
            if "symptoms" in query.lower():
                aspects.append("symptoms")
            if "causes" in query.lower():
                aspects.append("causes")
            if "treatments" in query.lower():
                aspects.append("treatments")
            
            # Generate a sub-question for each aspect
            for aspect in aspects:
                if aspect == "symptoms":
                    sub_questions.append(f"What are the symptoms of {entity}?")
                elif aspect == "causes":
                    sub_questions.append(f"What are the causes of {entity}?")
                elif aspect == "treatments":
                    sub_questions.append(f"What are the treatments for {entity}?")
            
            # Handle comparative aspects if present
            if "vs" in query.lower() or "compared" in query.lower():
                parts = query.lower().split("vs" if "vs" in query.lower() else "compared")
                if len(parts) == 2:
                    groups = [p.strip() for p in parts]
                    for group in groups:
                        sub_questions.append(f"What are the symptoms of {entity} in {group}?")
        return sub_questions
    
    def _extract_main_entity(self, text: str) -> str:
        """Extract the main entity from a text fragment"""
        # Remove common question words and verbs
        text = re.sub(r'\b(what|how|when|where|why|are|is|do|does|did)\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(symptoms|treatments|causes|of|for|compare|vs|versus)\b', '', text, flags=re.IGNORECASE)
        
        # Clean up the text
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        
        return text 