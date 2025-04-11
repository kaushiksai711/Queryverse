from pymongo import MongoClient
from typing import Optional, Dict, Any, Union
from src.utils.logger import setup_logger

class MongoDBConnector:
    def __init__(self, uri: str, db_name: str = "medical_chatbot"):
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.db = None
        self.logger = setup_logger("mongodb_connector")
    
    def is_connected(self) -> bool:
        """
        Check if the connector is connected to MongoDB.
        
        Returns:
            True if connected, False otherwise
        """
        return self.client is not None and self.db is not None
    
    def connect(self) -> bool:
        try:
            self.client = MongoClient(self.uri)
            # Test the connection
            self.client.admin.command('ping')
            # Initialize the database
            self.db = self.client[self.db_name]
            self.logger.info("Successfully connected to MongoDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            self.logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if self.client is None or self.db is None:
            raise Exception("Not connected to MongoDB")
        return self.db[collection_name]
    
    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> Union[str, bool]:
        """Insert a document into a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            self.logger.info(f"Inserted document into {collection_name}")
            return str(result.inserted_id)  # Return the ID of the inserted document
        except Exception as e:
            self.logger.error(f"Failed to insert document into {collection_name}: {str(e)}")
            return False
    
    def find_document(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a document in a collection"""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(query)
        except Exception as e:
            self.logger.error(f"Failed to find document in {collection_name}: {str(e)}")
            return None
    
    def update_document(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update a document in a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(query, {"$set": update})
            return result.modified_count > 0
        except Exception as e:
            self.logger.error(f"Failed to update document in {collection_name}: {str(e)}")
            return False
    
    def delete_document(self, collection_name: str, query: Dict[str, Any]) -> bool:
        """Delete a document from a collection"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            self.logger.error(f"Failed to delete document in {collection_name}: {str(e)}")
            return False