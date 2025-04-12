"""
Retrieval Agent for fetching information from knowledge bases.

This module contains the implementation of the retrieval agent
which is responsible for searching the knowledge base to find
relevant information for user queries.
"""

from typing import Dict, Any, List
from src.utils.logger import setup_logger
from sentence_transformers import SentenceTransformer
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector
from src.db.mongodb_connector import MongoDBConnector
import sys
import os

# Add MeTTa project path
metta_path = "/home/tanvi/MeTTaProject"
if os.path.exists(metta_path):
    sys.path.append(metta_path)

# Now you can import MeTTa modules
from metta_src import your_metta_module

class RetrievalAgent:
    """
    Agent responsible for retrieving information from knowledge bases.
    
    Responsibilities:
    - Search the knowledge graph for relevant entities
    - Perform semantic search using vector embeddings
    - Evaluate confidence in retrieval results
    - Handle simple query rewrites to improve search results
    """
    
    def __init__(self, neo4j: Neo4jConnector, qdrant: QdrantConnector, mongodb: MongoDBConnector):
        """
        Initialize the retrieval agent with required components.
        
        Args:
            neo4j: Manager for graph database operations
            qdrant: Service for vector embeddings and search
            mongodb: Manager for MongoDB operations
        """
        self.neo4j = neo4j
        self.qdrant = qdrant
        self.mongodb = mongodb
        self.logger = setup_logger("retrieval_agent")
        
        # Initialize sentence transformer model
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            self.logger.error(f"Error initializing sentence transformer: {str(e)}")
            raise
    
    def retrieve_knowledge(self, query: str) -> Dict[str, Any]:
        """
        Retrieve relevant knowledge from all available sources.
        
        Args:
            query: The user's query string
            
        Returns:
            Dict containing retrieved knowledge from different sources:
            - graph_data: Knowledge from Neo4j graph database
            - vector_data: Knowledge from Qdrant vector store
            - document_data: Knowledge from MongoDB document store
        """
        try:
            # Initialize result structure
            result = {
                "graph_data": [],
                "vector_data": [],
                "document_data": []
            }
            
            # Retrieve from graph database
            try:
                if self.neo4j.is_connected():
                    result["graph_data"] = self._retrieve_from_graph(query)
                else:
                    self.logger.warning("Not connected to Neo4j")
            except Exception as e:
                self.logger.error(f"Error retrieving from graph database: {str(e)}")
            
            # Retrieve from vector store
            try:
                if self.qdrant.is_connected():
                    result["vector_data"] = self._retrieve_from_vector(query)
                else:
                    self.logger.warning("Not connected to Qdrant")
            except Exception as e:
                self.logger.error(f"Error retrieving from vector store: {str(e)}")
            
            # Retrieve from document store
            try:
                if self.mongodb.is_connected():
                    result["document_data"] = self._retrieve_from_documents(query)
                else:
                    self.logger.warning("Not connected to MongoDB")
            except Exception as e:
                self.logger.error(f"Error retrieving from documents: {str(e)}")
            
            self.logger.info(f"Retrieved knowledge for query: {query}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in knowledge retrieval: {str(e)}")
            return {
                "error": str(e),
                "query": query
            }
    
    def _retrieve_from_graph(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from Neo4j graph database"""
        # Extract entities from query
        entities = self._extract_entities(query)
        
        # Get query intent
        intent = self._determine_intent(query)
        
        # Construct Cypher query based on entities and intent
        cypher_query = self._construct_cypher_query(entities, intent)
        
        # Execute query
        return self.neo4j.execute_query(cypher_query)
    
    def _retrieve_from_vector(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from Qdrant vector store"""
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()
        
        # Search in vector store
        return self.qdrant.search(query_vector, top_k=3)
    
    def _retrieve_from_documents(self, query: str) -> List[Dict[str, Any]]:
        """Retrieve relevant knowledge from MongoDB document store"""
        # Search in document store
        return self.mongodb.search_documents(query)
    
    def _extract_entities(self, query: str) -> List[str]:
        """
        Extract relevant entities from the query.
        
        This method identifies key entities in the query that should be used
        for searching in the knowledge base.
        
        Args:
            query: The user's query string
            
        Returns:
            List of extracted entities
        """
        # Common words to filter out
        common_words = [
            "what", "how", "when", "where", "why", "who", "which", "is", "are", "was", "were",
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "by",
            "about", "like", "as", "if", "then", "than", "that", "this", "these", "those",
            "my", "your", "his", "her", "its", "our", "their", "can", "could", "will", "would",
            "should", "may", "might", "must", "have", "has", "had", "do", "does", "did",
            "tell", "me", "show", "give", "find", "search", "look", "up", "information", "about"
        ]
        
        # Split the query into words and filter out common words
        words = query.lower().split()
        entities = [word for word in words if word.lower() not in common_words]
        
        # If no entities found, try to use the whole query as an entity
        if not entities:
            entities = [query.lower()]
            
        return entities
    
    def _construct_cypher_query(self, entities: List[str], intent: str = None) -> str:
        """
        Construct Cypher query based on extracted entities and intent.
        
        This method creates a Cypher query that searches for entities not only
        in the main node but also in related nodes.
        
        Args:
            entities: List of entities to search for
            intent: The intent of the query (e.g., treatment, symptoms)
            
        Returns:
            A Cypher query string
        """
        if not entities:
            return "MATCH (n) RETURN n LIMIT 5"
        
        # Construct a more sophisticated pattern matching query
        entity_pattern = "|".join(entities)
        
        # Base query to find the disease/condition with more flexible matching
        base_query = f"""
        MATCH (d:Disease)
        WHERE d.name =~ '(?i).*({entity_pattern}).*' 
           OR d.name =~ '(?i)({entity_pattern}).*'
           OR d.name =~ '(?i).*({entity_pattern})'
           OR d.name =~ '(?i)({entity_pattern})'
        """
        
        # Add relationship based on intent
        if intent == "treatment":
            # Create a query that first finds the closest match, then gets treatments
            return f"""
            // Find the most similar disease first
            MATCH (d:Disease)
            WITH d, apoc.text.levenshteinSimilarity(toLower(d.name), toLower('{entities[0]}')) as similarity
            ORDER BY similarity DESC
            LIMIT 1
            
            // Then get its treatments
            MATCH (d)-[:TREATED_BY]->(t:Treatment)
            WITH d, COLLECT({{
                name: t.name,
                description: t.description
            }}) as treatments
            
            // Return the disease and its treatments
            RETURN d.name as disease,
                   d.description as description,
                   treatments
            """
        elif intent == "symptoms":
            return f"""
            {base_query}
            OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:Symptom)
            WHERE s.name =~ '(?i).*({entity_pattern}).*' OR s.description =~ '(?i).*({entity_pattern}).*'
            RETURN d.name as disease, d.description as description, 
                   'HAS_SYMPTOM' as relationship, s.name as related_node, s.description as related_description
            UNION
            MATCH (s:Symptom)
            WHERE s.name =~ '(?i).*({entity_pattern}).*' OR s.description =~ '(?i).*({entity_pattern}).*'
            OPTIONAL MATCH (d:Disease)-[:HAS_SYMPTOM]->(s)
            RETURN d.name as disease, d.description as description, 
                   'HAS_SYMPTOM' as relationship, s.name as related_node, s.description as related_description
            LIMIT 10
            """
        elif intent == "diagnosis":
            return f"""
            {base_query}
            OPTIONAL MATCH (d)-[:HAS_DIAGNOSIS]->(diag:Diagnosis)
            WHERE diag.name =~ '(?i).*({entity_pattern}).*' OR diag.description =~ '(?i).*({entity_pattern}).*'
            RETURN d.name as disease, d.description as description, 
                   'HAS_DIAGNOSIS' as relationship, diag.name as related_node, diag.description as related_description
            UNION
            MATCH (diag:Diagnosis)
            WHERE diag.name =~ '(?i).*({entity_pattern}).*' OR diag.description =~ '(?i).*({entity_pattern}).*'
            OPTIONAL MATCH (d:Disease)-[:HAS_DIAGNOSIS]->(diag)
            RETURN d.name as disease, d.description as description, 
                   'HAS_DIAGNOSIS' as relationship, diag.name as related_node, diag.description as related_description
            LIMIT 10
            """
        elif intent == "prevention":
            return f"""
            {base_query}
            OPTIONAL MATCH (d)-[:HAS_PREVENTION]->(p:Prevention)
            WHERE p.name =~ '(?i).*({entity_pattern}).*' OR p.description =~ '(?i).*({entity_pattern}).*'
            RETURN d.name as disease, d.description as description, 
                   'HAS_PREVENTION' as relationship, p.name as related_node, p.description as related_description
            UNION
            MATCH (p:Prevention)
            WHERE p.name =~ '(?i).*({entity_pattern}).*' OR p.description =~ '(?i).*({entity_pattern}).*'
            OPTIONAL MATCH (d:Disease)-[:HAS_PREVENTION]->(p)
            RETURN d.name as disease, d.description as description, 
                   'HAS_PREVENTION' as relationship, p.name as related_node, p.description as related_description
            LIMIT 10
            """
        else:
            # Default to general information with all related nodes
            return f"""
            {base_query}
            OPTIONAL MATCH (d)-[r]->(n)
            WHERE n.name =~ '(?i).*({entity_pattern}).*' OR n.description =~ '(?i).*({entity_pattern}).*'
            RETURN d.name as disease, d.description as description,
                   type(r) as relationship, n.name as related_node, n.description as related_description
            UNION
            MATCH (n)
            WHERE n.name =~ '(?i).*({entity_pattern}).*' OR n.description =~ '(?i).*({entity_pattern}).*'
            OPTIONAL MATCH (d:Disease)-[r]->(n)
            RETURN d.name as disease, d.description as description,
                   type(r) as relationship, n.name as related_node, n.description as related_description
            LIMIT 15
            """
    
    async def retrieve(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Retrieve relevant information from knowledge bases.
        
        This method searches for information about the query in both the vector
        database and the graph database, and combines the results.
        
        Args:
            query: The user's query string
            context: Optional context information
            
        Returns:
            Dict containing retrieved knowledge and sources
        """
        try:
            # Extract entities for more targeted search
            entities = self._extract_entities(query)
            
            # Generate query embedding
            query_vector = self.model.encode(query).tolist()
            
            # Get vector search results with lower threshold for more results
            vector_results = []
            if self.qdrant.is_connected():
                # Try with the full query first
                vector_results = self.qdrant.search(
                    query_vector=query_vector,
                    limit=5,
                    score_threshold=0.5  # Lower threshold to get more results
                )
                
                # If no results, try with each entity
                if not vector_results and entities:
                    for entity in entities:
                        entity_vector = self.model.encode(entity).tolist()
                        entity_results = self.qdrant.search(
                            query_vector=entity_vector,
                            limit=3,
                            score_threshold=0.5
                        )
                        vector_results.extend(entity_results)
            else:
                self.logger.warning("Qdrant not connected")
            
            # Get graph search results
            graph_results = []
            if self.neo4j.is_connected():
                intent = self._determine_intent(query)
                cypher_query = self._construct_cypher_query(entities, intent)
                self.logger.debug(f"Executing Cypher query: {cypher_query}")
                graph_results = self.neo4j.execute_query(cypher_query)
            else:
                self.logger.warning("Neo4j not connected")
            
            # Combine and rank results
            combined_results = []
            sources = set()
            
            # Process vector results
            if vector_results:
                for result in vector_results:
                    combined_results.append({
                        "source": "vector",
                        "content": result.get("content", ""),
                        "metadata": result.get("metadata", {}),
                        "score": result.get("score", 0.0)
                    })
                    sources.add("vector")
            
            # Process graph results
            if graph_results:
                for result in graph_results:
                    combined_results.append({
                        "source": "graph",
                        "content": str(result),
                        "metadata": {},
                        "score": 0.8  # Default high score for graph results
                    })
                    sources.add("graph")
            
            # Sort by score
            combined_results.sort(key=lambda x: x["score"], reverse=True)
            
            # If no results found, return a helpful message
            if not combined_results:
                return {
                    "status": "success",
                    "knowledge": "I couldn't find specific information about that in my knowledge base. Could you please rephrase your question or provide more details?",
                    "sources": list(sources)
                }
            
            # Return the top results
            return {
                "status": "success",
                "knowledge": combined_results[:10],  # Return top 10 results
                "sources": list(sources)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving information: {str(e)}")
            return {
                "status": "error",
                "knowledge": "Error retrieving information",
                "error": str(e)
            }
    
    def _semantic_search(self, query):
        """
        Perform semantic search using vector embeddings.
        
        Args:
            query: Interpreted query object
            
        Returns:
            List of semantic search results
        """
        # In Phase 1, this will use mock data
        query_text = query.get('text', '')
        
        # Mock implementation
        return self.embedding_service.search(query_text, top_k=5)
    
    def _graph_search(self, query):
        """
        Search for entities in the knowledge graph.
        
        Args:
            query: Interpreted query object
            
        Returns:
            List of graph search results
        """
        # In Phase 1, this will use mock data
        entities = query.get('entities', [])
        
        # Mock implementation
        results = []
        for entity in entities:
            graph_result = self.graph_manager.find_entity(entity)
            if graph_result:
                results.append(graph_result)
        
        return results
    
    def _combine_results(self, semantic_results, graph_results):
        """
        Combine results from different search strategies.
        
        Args:
            semantic_results: Results from semantic search
            graph_results: Results from graph search
            
        Returns:
            Combined and ranked results
        """
        # Simple combination for Phase 1
        combined = []
        
        # Add graph results first (usually more precise)
        combined.extend(graph_results)
        
        # Add semantic results that aren't duplicates
        existing_ids = {r.get('id') for r in combined if 'id' in r}
        for result in semantic_results:
            if result.get('id') not in existing_ids:
                combined.append(result)
        
        return combined
    
    def _calculate_confidence(self, results):
        """
        Calculate a confidence score for the retrieval results.
        
        Args:
            results: Combined search results
            
        Returns:
            Confidence score between 0 and 1
        """
        # Simple implementation for Phase 1
        if not results:
            return 0.0
        
        # Average the relevance scores of top 3 results
        top_results = results[:3]
        scores = [r.get('score', 0) for r in top_results if 'score' in r]
        
        if not scores:
            return 0.3  # Default low confidence if no scores available
        
        return sum(scores) / len(scores)
    
    def _extract_sources(self, results):
        """
        Extract source information from results for attribution.
        
        Args:
            results: Combined search results
            
        Returns:
            List of source information
        """
        sources = []
        for result in results:
            if 'source' in result:
                source = result['source']
                if source not in sources:
                    sources.append(source)
        
        return sources
    
    def _determine_intent(self, query: str) -> str:
        """Determine the intent of the query"""
        query = query.lower()
        if any(word in query for word in ["treat", "treatment", "medicine", "medication"]):
            return "treatment"
        elif any(word in query for word in ["symptom", "sign", "manifestation"]):
            return "symptoms"
        elif any(word in query for word in ["diagnose", "diagnosis", "cause", "why"]):
            return "diagnosis"
        elif any(word in query for word in ["prevent", "prevention", "avoid"]):
            return "prevention"
        return None 

    def _format_response(self, knowledge: Dict[str, Any]) -> str:
        """
        Format the knowledge into a clean response for OpenRouter.
        
        Args:
            knowledge: Dict containing retrieved knowledge
            
        Returns:
            Formatted response string
        """
        if not knowledge.get("knowledge"):
            return "I couldn't find any information about that disease or its treatments."
            
        knowledge_data = knowledge["knowledge"]
        if not knowledge_data:
            return "I couldn't find any information about that disease or its treatments."
            
        # Get the first (most similar) result
        result = knowledge_data[0] if isinstance(knowledge_data, list) else knowledge_data
        
        if not isinstance(result, dict):
            return "I couldn't find any information about that disease or its treatments."
            
        disease = result.get("disease", "")
        description = result.get("description", "")
        treatments = result.get("treatments", [])
        
        if not disease:
            return "I couldn't find any information about that disease or its treatments."
            
        # Format the response
        response_parts = []
        
        # Add disease information
        if description:
            response_parts.append(f"{disease}: {description}")
        else:
            response_parts.append(disease)
            
        # Add treatments if available
        if treatments:
            response_parts.append("\nTreatments:")
            for treatment in treatments:
                if isinstance(treatment, dict):
                    name = treatment.get("name", "")
                    desc = treatment.get("description", "")
                    if name:
                        if desc:
                            response_parts.append(f"- {name}: {desc}")
                        else:
                            response_parts.append(f"- {name}")
        else:
            response_parts.append("\nNo specific treatments found for this condition.")
            
        return "\n".join(response_parts) 