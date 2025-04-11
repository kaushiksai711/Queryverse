"""
Orchestrator module for coordinating workflow between agents.

This module contains the main orchestrator class that coordinates
the interaction between the query interpreter, retrieval agent,
and renderer components.
"""

from typing import Dict, Any
from src.utils.logger import setup_logger
from src.agents.query_interpreter import QueryInterpreter
from src.agents.query_decomposer import QueryDecomposer
from src.agents.retrieval_agent import RetrievalAgent

class Orchestrator:
    """
    Orchestrator class for coordinating the workflow between different agents.
    
    Responsibilities:
    - Coordinate the workflow between query interpreter and retrieval agent
    - Manage the processing pipeline for user queries
    - Control the flow of information between components
    - Deliver final responses using appropriate renderers
    """
    
    def __init__(self, query_interpreter: QueryInterpreter, query_decomposer: QueryDecomposer, retrieval_agent: RetrievalAgent):
        """Initialize the orchestrator with required agents"""
        self.query_interpreter = query_interpreter
        self.query_decomposer = query_decomposer
        self.retrieval_agent = retrieval_agent
        self.logger = setup_logger("orchestrator")
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the complete workflow.
        
        Args:
            query: The user's query string
            
        Returns:
            Dict containing processing results including:
            - type: The type of query (single or complex)
            - query: The original query
            - interpretation: The query interpretation
            - sub_questions: List of decomposed sub-questions (if complex)
            - results: List of results for each sub-question (if complex)
            - knowledge: Retrieved knowledge (if single)
            - response: The final response text
            - sources: List of sources used for the response
        """
        try:
            # Step 1: Interpret the query
            interpretation = await self.query_interpreter.interpret(query)
            self.logger.info(f"Query interpretation: {interpretation}")
            
            # Step 2: Decompose the query if complex
            decomposition = await self.query_decomposer.decompose(query)
            
            if decomposition["is_complex"]:
                # Process complex query
                results = []
                responses = []
                all_sources = set()
                for sub_question in decomposition["sub_questions"]:
                    sub_result = await self.retrieval_agent.retrieve(sub_question)
                    results.append({
                        "question": sub_question,
                        "knowledge": sub_result
                    })
                    if "response" in sub_result:
                        responses.append(sub_result["response"])
                    if "sources" in sub_result:
                        all_sources.update(sub_result["sources"])
                
                return {
                    "type": "complex",
                    "query": query,
                    "interpretation": interpretation,
                    "sub_questions": decomposition["sub_questions"],
                    "results": results,
                    "response": " ".join(responses) if responses else "No information found",
                    "sources": list(all_sources)
                }
            else:
                # Process single query
                knowledge = await self.retrieval_agent.retrieve(query)
                
                return {
                    "type": "single",
                    "query": query,
                    "interpretation": interpretation,
                    "knowledge": knowledge,
                    "response": knowledge.get("response", "No information found"),
                    "sources": knowledge.get("sources", [])
                }
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return {
                "error": str(e),
                "query": query,
                "response": f"Error processing query: {str(e)}",
                "sources": []
            } 