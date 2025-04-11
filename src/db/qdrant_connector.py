"""
Qdrant connector for vector database functionality.

This module provides a real implementation of a Qdrant connector
that connects to a Qdrant vector database instance.
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Union
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition,
    Range, MatchValue, CollectionInfo
)

logger = logging.getLogger(__name__)

class QdrantConnector:
    """
    Connector for Qdrant vector database.
    
    Responsibilities:
    - Connect to Qdrant vector database
    - Upload and manage vector embeddings
    - Perform vector similarity search
    - Associate metadata with vectors
    """
    
    def __init__(self, url: str, api_key: Optional[str] = None, collection_name: str = "medical_knowledge"):
        """
        Initialize the Qdrant connector.
        
        Args:
            url: Qdrant service URL
            api_key: Optional API key for authentication
            collection_name: Collection name to use
        """
        self.url = url or "https://90c18eba-c9f7-489f-9371-b46eea57639f.eu-central-1-0.aws.cloud.qdrant.io:6333"
        self.api_key = api_key or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.4UBgGua3TwRyilImpsJkdkD0spqfhfyr4xld3aASbOU"
        self.collection_name = collection_name or "medical_knowledge"
        self.client = None
        self.connected = False
        self.vector_size = 384  # Default for SentenceTransformers models
        
        logger.info(f"Initializing Qdrant connector to {self.url} with collection {self.collection_name}")
    
    def is_connected(self) -> bool:
        """
        Check if the connector is connected to Qdrant.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected and self.client is not None
    
    def connect(self) -> bool:
        """
        Connect to Qdrant.
        
        Returns:
            True if connection successful
        """
        try:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key
            )
            # Verify connection by getting collection info
            self.client.get_collection(self.collection_name)
            self.connected = True
            logger.info("Connected to Qdrant")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """
        Disconnect from Qdrant.
        """
        if self.client:
            # Qdrant client doesn't have an explicit close method
            # but we can reset the client and connection state
            self.client = None
            self.connected = False
            logger.info("Disconnected from Qdrant")
    
    def create_collection(self, vector_size: int = 384, distance: str = "Cosine") -> bool:
        """
        Create a new collection for vector storage.
        
        Args:
            vector_size: Dimension of vectors
            distance: Distance metric ("Cosine", "Euclid", or "Dot")
            
        Returns:
            True if creation successful
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return False
        
        self.vector_size = vector_size
        
        try:
            # Check if collection already exists
            collections = self.client.get_collections()
            if self.collection_name in [c.name for c in collections.collections]:
                logger.info(f"Collection {self.collection_name} already exists")
                return True
            
            # Map distance string to Distance enum
            distance_map = {
                "Cosine": "Cosine",
                "Euclid": "Euclidean",
                "Dot": "Dot"
            }
            distance_type = distance_map.get(distance, "Cosine")
            
            # Create collection with specified parameters
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance_type)
            )
            logger.info(f"Created collection {self.collection_name} with vector size {vector_size}")
            return True
        except Exception as e:
            logger.error(f"Error creating collection: {str(e)}")
            return False
    
    def delete_collection(self) -> bool:
        """
        Delete the collection.
        
        Returns:
            True if deletion successful
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return False
        
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            logger.info(f"Deleted collection {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            return False
    
    def get_collection_info(self) -> Optional[CollectionInfo]:
        """
        Get information about the collection.
        
        Returns:
            Collection information or None if error
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return None
        
        try:
            return self.client.get_collection(collection_name=self.collection_name)
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return None
    
    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Insert or update a vector in the collection.
        
        Args:
            id: Unique identifier for the vector
            vector: Vector to store
            metadata: Associated metadata
            
        Returns:
            True if operation successful
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return False
        
        try:
            # Convert string ID to a unique integer ID if needed
            point_id = id if isinstance(id, int) else hash(id) & 0xffffffff
            
            # Create point with vector and metadata
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=metadata or {}
            )
            
            # Insert the point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Upserted vector for ID: {id}")
            return True
        except Exception as e:
            logger.error(f"Error upserting vector: {str(e)}")
            return False
    
    def batch_upsert(self, items: List[Dict[str, Any]]) -> bool:
        """
        Insert or update multiple vectors in batch.
        
        Args:
            items: List of dictionaries with id, vector, and metadata
            
        Returns:
            True if operation successful
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return False
        
        try:
            points = []
            for item in items:
                # Convert string ID to a unique integer ID if needed
                point_id = item['id'] if isinstance(item['id'], int) else hash(item['id']) & 0xffffffff
                
                point = PointStruct(
                    id=point_id,
                    vector=item['vector'],
                    payload=item.get('metadata', {})
                )
                points.append(point)
            
            # Insert the points in batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Batch upserted {len(points)} vectors")
            return True
        except Exception as e:
            logger.error(f"Error batch upserting vectors: {str(e)}")
            return False
    
    def search(self, vector: List[float], top_k: int = 5, 
              filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            vector: Query vector
            top_k: Number of results to return
            filters: Optional filters to apply
            
        Returns:
            List of search results with similarity scores
        """
        if not self.connected or not self.client:
            logger.warning("Not connected to Qdrant")
            return []
        
        try:
            # Convert filters to Qdrant filter format
            qdrant_filter = self._convert_filters(filters) if filters else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=vector,
                limit=top_k,
                query_filter=qdrant_filter
            )
            
            # Format results
            results = []
            for result in search_results:
                result_dict = {
                    "id": result.id,
                    "score": result.score,
                    "metadata": result.payload
                }
                results.append(result_dict)
            
            return results
        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []
    
    def _convert_filters(self, filters: Dict[str, Any]) -> Filter:
        """
        Convert simple filters to Qdrant filter format.
        
        Args:
            filters: Dictionary of filter conditions
            
        Returns:
            Qdrant Filter object
        """
        if not filters:
            return None
        
        conditions = []
        
        for field, value in filters.items():
            if isinstance(value, list):
                # For list values, use any match
                conditions.append(FieldCondition(
                    key=field,
                    match=MatchValue(any=value)
                ))
            elif isinstance(value, dict) and ('min' in value or 'max' in value):
                # For range values
                range_kwargs = {}
                if 'min' in value:
                    range_kwargs['gte'] = value['min']
                if 'max' in value:
                    range_kwargs['lte'] = value['max']
                
                conditions.append(FieldCondition(
                    key=field,
                    range=Range(**range_kwargs)
                ))
            else:
                # For exact match
                conditions.append(FieldCondition(
                    key=field,
                    match=MatchValue(value=value)
                ))
        
        return Filter(must=conditions)
    
    def execute_medical_data_setup(self, vector_size: int = 384) -> bool:
        """
        Set up the collection for medical data vectors.
        
        Args:
            vector_size: Dimension of the vectors
            
        Returns:
            True if setup successful
        """
        if not self.connected:
            logger.warning("Not connected to Qdrant")
            return False
        
        try:
            # Create or recreate the collection
            self.vector_size = vector_size
            return self.create_collection(vector_size=vector_size)
        except Exception as e:
            logger.error(f"Error setting up medical data collection: {str(e)}")
            return False 