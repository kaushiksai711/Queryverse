"""
Medical data loader utility.

This module provides functions to populate the Neo4j and Qdrant databases
with medical knowledge data, including diseases, symptoms, treatments, and their relationships.
"""

import logging
import os
import json
import random
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector

logger = logging.getLogger(__name__)

# Sample medical data
DISEASES = [
    {
        "id": "disease_diabetes",
        "name": "Diabetes Mellitus",
        "description": "A metabolic disease that causes high blood sugar levels due to problems with insulin production or action.",
        "icd10": "E10-E14",
        "categories": ["endocrine", "metabolic"],
        "prevalence": "High",
        "risk_factors": ["obesity", "family history", "age", "physical inactivity"]
    },
    {
        "id": "disease_hypertension",
        "name": "Hypertension",
        "description": "A condition in which the force of the blood against the artery walls is too high, often leading to heart disease.",
        "icd10": "I10-I15",
        "categories": ["cardiovascular"],
        "prevalence": "Very high",
        "risk_factors": ["age", "obesity", "high sodium intake", "stress", "family history"]
    },
    {
        "id": "disease_asthma",
        "name": "Asthma",
        "description": "A chronic disease involving the airways in the lungs, causing breathing difficulty due to inflammation and narrowing of air passages.",
        "icd10": "J45",
        "categories": ["respiratory"],
        "prevalence": "Moderate",
        "risk_factors": ["allergies", "family history", "air pollution", "smoking"]
    },
    {
        "id": "disease_hypothyroidism",
        "name": "Hypothyroidism",
        "description": "A condition in which the thyroid gland doesn't produce enough thyroid hormone, leading to various symptoms.",
        "icd10": "E03",
        "categories": ["endocrine"],
        "prevalence": "Moderate",
        "risk_factors": ["autoimmune disease", "thyroid surgery", "radiation therapy", "certain medications"]
    },
    {
        "id": "disease_pneumonia",
        "name": "Pneumonia",
        "description": "An infection that inflames the air sacs in one or both lungs, which may fill with fluid.",
        "icd10": "J12-J18",
        "categories": ["respiratory", "infectious"],
        "prevalence": "Moderate",
        "risk_factors": ["weak immune system", "age", "smoking", "hospitalization", "chronic disease"]
    }
]

SYMPTOMS = [
    {
        "id": "symptom_fatigue",
        "name": "Fatigue",
        "description": "A feeling of tiredness, exhaustion, or lack of energy.",
        "severity": "Varies",
        "common_causes": ["stress", "lack of sleep", "anemia", "depression", "chronic illness"]
    },
    {
        "id": "symptom_fever",
        "name": "Fever",
        "description": "An elevated body temperature above the normal range of 36-37°C (98-100°F), often indicating infection.",
        "severity": "Moderate",
        "common_causes": ["infection", "inflammation", "heat exhaustion", "certain medications"]
    },
    {
        "id": "symptom_headache",
        "name": "Headache",
        "description": "Pain in the head or upper neck, which can be a symptom of various conditions or a primary disorder.",
        "severity": "Mild to severe",
        "common_causes": ["stress", "dehydration", "eyestrain", "sinus congestion", "migraine"]
    },
    {
        "id": "symptom_increased_thirst",
        "name": "Increased Thirst",
        "description": "Abnormal feeling of needing to drink fluids, often due to dehydration or medical conditions.",
        "severity": "Mild",
        "common_causes": ["dehydration", "diabetes", "medication side effects", "excessive sweating"]
    },
    {
        "id": "symptom_shortness_of_breath",
        "name": "Shortness of Breath",
        "description": "Difficulty breathing or a feeling of not getting enough air, also known as dyspnea.",
        "severity": "Moderate to severe",
        "common_causes": ["asthma", "anxiety", "heart failure", "pneumonia", "physical exertion"]
    },
    {
        "id": "symptom_cough",
        "name": "Cough",
        "description": "A sudden, often repetitive, spasmodic expulsion of air from the lungs.",
        "severity": "Mild to severe",
        "common_causes": ["upper respiratory infection", "asthma", "allergies", "GERD", "smoking"]
    },
    {
        "id": "symptom_chest_pain",
        "name": "Chest Pain",
        "description": "Discomfort or pain felt in the chest area, which may indicate various conditions including heart problems.",
        "severity": "Moderate to severe",
        "common_causes": ["angina", "heart attack", "pulmonary embolism", "anxiety", "muscle strain"]
    }
]

TREATMENTS = [
    {
        "id": "treatment_insulin_therapy",
        "name": "Insulin Therapy",
        "description": "The administration of insulin to maintain proper blood glucose levels in patients with diabetes.",
        "type": "medication",
        "method": "injection"
    },
    {
        "id": "treatment_diet_modification",
        "name": "Diet Modification",
        "description": "Changes to dietary habits to manage various health conditions.",
        "type": "lifestyle",
        "method": "diet"
    },
    {
        "id": "treatment_blood_pressure_medication",
        "name": "Blood Pressure Medication",
        "description": "Medications designed to lower and manage high blood pressure.",
        "type": "medication",
        "method": "oral"
    },
    {
        "id": "treatment_inhaler",
        "name": "Inhaler Therapy",
        "description": "The use of inhalers to deliver medication directly to the lungs to treat respiratory conditions.",
        "type": "medication",
        "method": "inhalation"
    },
    {
        "id": "treatment_thyroid_hormone",
        "name": "Thyroid Hormone Replacement",
        "description": "Synthetic thyroid hormones used to treat hypothyroidism.",
        "type": "medication",
        "method": "oral"
    },
    {
        "id": "treatment_antibiotics",
        "name": "Antibiotic Treatment",
        "description": "Medications used to treat bacterial infections by killing or inhibiting the growth of bacteria.",
        "type": "medication",
        "method": "various"
    }
]

# Define relationships between entities
DISEASE_SYMPTOM_RELATIONSHIPS = [
    {"from_id": "disease_diabetes", "to_id": "symptom_increased_thirst", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "moderate"}},
    {"from_id": "disease_diabetes", "to_id": "symptom_fatigue", "type": "EXHIBITS", "properties": {"frequency": "common", "specificity": "low"}},
    {"from_id": "disease_hypertension", "to_id": "symptom_headache", "type": "EXHIBITS", "properties": {"frequency": "common", "specificity": "low"}},
    {"from_id": "disease_hypertension", "to_id": "symptom_chest_pain", "type": "EXHIBITS", "properties": {"frequency": "less common", "specificity": "moderate"}},
    {"from_id": "disease_asthma", "to_id": "symptom_shortness_of_breath", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "high"}},
    {"from_id": "disease_asthma", "to_id": "symptom_cough", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "moderate"}},
    {"from_id": "disease_hypothyroidism", "to_id": "symptom_fatigue", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "low"}},
    {"from_id": "disease_pneumonia", "to_id": "symptom_fever", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "moderate"}},
    {"from_id": "disease_pneumonia", "to_id": "symptom_cough", "type": "EXHIBITS", "properties": {"frequency": "very common", "specificity": "moderate"}},
    {"from_id": "disease_pneumonia", "to_id": "symptom_shortness_of_breath", "type": "EXHIBITS", "properties": {"frequency": "common", "specificity": "moderate"}}
]

DISEASE_TREATMENT_RELATIONSHIPS = [
    {"from_id": "disease_diabetes", "to_id": "treatment_insulin_therapy", "type": "TREATED_BY", "properties": {"effectiveness": "high", "common_first_line": True}},
    {"from_id": "disease_diabetes", "to_id": "treatment_diet_modification", "type": "TREATED_BY", "properties": {"effectiveness": "moderate", "common_first_line": True}},
    {"from_id": "disease_hypertension", "to_id": "treatment_blood_pressure_medication", "type": "TREATED_BY", "properties": {"effectiveness": "high", "common_first_line": True}},
    {"from_id": "disease_hypertension", "to_id": "treatment_diet_modification", "type": "TREATED_BY", "properties": {"effectiveness": "moderate", "common_first_line": True}},
    {"from_id": "disease_asthma", "to_id": "treatment_inhaler", "type": "TREATED_BY", "properties": {"effectiveness": "high", "common_first_line": True}},
    {"from_id": "disease_hypothyroidism", "to_id": "treatment_thyroid_hormone", "type": "TREATED_BY", "properties": {"effectiveness": "high", "common_first_line": True}},
    {"from_id": "disease_pneumonia", "to_id": "treatment_antibiotics", "type": "TREATED_BY", "properties": {"effectiveness": "high", "common_first_line": True}}
]

class MedicalDataLoader:
    """
    Utility for loading medical data into Neo4j and Qdrant databases.
    """
    
    def __init__(self, 
                 neo4j_connector: Neo4jConnector, 
                 qdrant_connector: QdrantConnector,
                 embedding_model: Optional[str] = None):
        """
        Initialize the medical data loader.
        
        Args:
            neo4j_connector: Initialized Neo4j connector
            qdrant_connector: Initialized Qdrant connector
            embedding_model: Name of the SentenceTransformer model to use
        """
        self.neo4j = neo4j_connector
        self.qdrant = qdrant_connector
        
        # Initialize embedding model
        self.model_name = embedding_model or "all-MiniLM-L6-v2"
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.warning(f"Could not load embedding model {self.model_name}: {str(e)}")
            logger.warning("Will use random embeddings instead")
            self.model = None
    
    def load_all_data(self) -> bool:
        """
        Load all medical data into the databases.
        
        Returns:
            True if data loading was successful
        """
        logger.info("Starting medical data loading process")
        
        # Check connections
        if not self.neo4j.connected or not self.qdrant.connected:
            logger.error("Database connections not established")
            return False
        
        # Set up database schemas
        if not self.neo4j.execute_medical_data_setup():
            logger.error("Failed to set up Neo4j schema")
            return False
        
        if not self.qdrant.execute_medical_data_setup():
            logger.error("Failed to set up Qdrant collection")
            return False
        
        # Load diseases
        logger.info("Loading diseases")
        if not self._load_diseases():
            logger.error("Failed to load diseases")
            return False
        
        # Load symptoms
        logger.info("Loading symptoms")
        if not self._load_symptoms():
            logger.error("Failed to load symptoms")
            return False
        
        # Load treatments
        logger.info("Loading treatments")
        if not self._load_treatments():
            logger.error("Failed to load treatments")
            return False
        
        # Create relationships
        logger.info("Creating relationships")
        if not self._create_relationships():
            logger.error("Failed to create relationships")
            return False
        
        logger.info("Medical data loading completed successfully")
        return True
    
    def _load_diseases(self) -> bool:
        """
        Load disease data into Neo4j and Qdrant.
        
        Returns:
            True if successful
        """
        try:
            # Load diseases into Neo4j
            for disease in DISEASES:
                # Create disease node in Neo4j
                self.neo4j.create_entity(
                    labels=["Entity", "Disease"], 
                    properties=disease
                )
                
                # Create disease vector in Qdrant
                vector = self._get_embedding(f"{disease['name']}: {disease['description']}")
                self.qdrant.upsert(
                    id=disease['id'],
                    vector=vector,
                    metadata={
                        "id": disease['id'],
                        "name": disease['name'],
                        "description": disease['description'],
                        "type": "disease",
                        "categories": disease.get('categories', [])
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Error loading diseases: {str(e)}")
            return False
    
    def _load_symptoms(self) -> bool:
        """
        Load symptom data into Neo4j and Qdrant.
        
        Returns:
            True if successful
        """
        try:
            # Load symptoms into Neo4j
            for symptom in SYMPTOMS:
                # Create symptom node in Neo4j
                self.neo4j.create_entity(
                    labels=["Entity", "Symptom"], 
                    properties=symptom
                )
                
                # Create symptom vector in Qdrant
                vector = self._get_embedding(f"{symptom['name']}: {symptom['description']}")
                self.qdrant.upsert(
                    id=symptom['id'],
                    vector=vector,
                    metadata={
                        "id": symptom['id'],
                        "name": symptom['name'],
                        "description": symptom['description'],
                        "type": "symptom",
                        "severity": symptom.get('severity', 'Unknown')
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Error loading symptoms: {str(e)}")
            return False
    
    def _load_treatments(self) -> bool:
        """
        Load treatment data into Neo4j and Qdrant.
        
        Returns:
            True if successful
        """
        try:
            # Load treatments into Neo4j
            for treatment in TREATMENTS:
                # Create treatment node in Neo4j
                self.neo4j.create_entity(
                    labels=["Entity", "Treatment"], 
                    properties=treatment
                )
                
                # Create treatment vector in Qdrant
                vector = self._get_embedding(f"{treatment['name']}: {treatment['description']}")
                self.qdrant.upsert(
                    id=treatment['id'],
                    vector=vector,
                    metadata={
                        "id": treatment['id'],
                        "name": treatment['name'],
                        "description": treatment['description'],
                        "type": "treatment",
                        "treatment_type": treatment.get('type', 'Unknown')
                    }
                )
            
            return True
        except Exception as e:
            logger.error(f"Error loading treatments: {str(e)}")
            return False
    
    def _create_relationships(self) -> bool:
        """
        Create relationships between entities in Neo4j.
        
        Returns:
            True if successful
        """
        try:
            # Create disease-symptom relationships
            for rel in DISEASE_SYMPTOM_RELATIONSHIPS:
                self.neo4j.create_relationship(
                    from_id=rel['from_id'],
                    to_id=rel['to_id'],
                    rel_type=rel['type'],
                    properties=rel['properties']
                )
            
            # Create disease-treatment relationships
            for rel in DISEASE_TREATMENT_RELATIONSHIPS:
                self.neo4j.create_relationship(
                    from_id=rel['from_id'],
                    to_id=rel['to_id'],
                    rel_type=rel['type'],
                    properties=rel['properties']
                )
            
            return True
        except Exception as e:
            logger.error(f"Error creating relationships: {str(e)}")
            return False
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        if self.model:
            try:
                # Use sentence transformer model
                return self.model.encode(text).tolist()
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                # Fall back to random embedding
                
        # Use random embedding if model not available or failed
        vector_size = self.qdrant.vector_size
        random_vector = np.random.rand(vector_size).astype(np.float32)
        # Normalize to unit length for cosine similarity
        random_vector = random_vector / np.linalg.norm(random_vector)
        return random_vector.tolist()


def populate_medical_data(neo4j_uri: str, neo4j_user: str, neo4j_password: str,
                          qdrant_url: str, qdrant_api_key: Optional[str] = None) -> bool:
    """
    Populate the databases with medical data.
    
    Args:
        neo4j_uri: URI for Neo4j database
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        qdrant_url: URL for Qdrant service
        qdrant_api_key: Optional API key for Qdrant
        
    Returns:
        True if data population was successful
    """
    try:
        # Initialize connectors
        neo4j_connector = Neo4jConnector(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password
        )
        
        qdrant_connector = QdrantConnector(
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name="medical_knowledge"
        )
        
        # Connect to databases
        if not neo4j_connector.connect():
            logger.error("Failed to connect to Neo4j")
            return False
        
        if not qdrant_connector.connect():
            logger.error("Failed to connect to Qdrant")
            neo4j_connector.disconnect()
            return False
        
        # Initialize data loader
        loader = MedicalDataLoader(
            neo4j_connector=neo4j_connector,
            qdrant_connector=qdrant_connector
        )
        
        # Load data
        success = loader.load_all_data()
        
        # Disconnect
        neo4j_connector.disconnect()
        qdrant_connector.disconnect()
        
        return success
        
    except Exception as e:
        logger.error(f"Error in medical data population: {str(e)}")
        return False


if __name__ == "__main__":
    # This allows running the script directly
    from src.utils.logger import setup_logger
    
    # Set up logging
    setup_logger("src.utils.medical_data_loader")
    
    # Get database credentials from environment
    neo4j_uri = os.environ.get("NEO4J_URI", "")
    neo4j_user = os.environ.get("NEO4J_USER", "")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "")
    
    qdrant_url = os.environ.get("QDRANT_URL", "")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY", None)
    
    if not neo4j_uri or not neo4j_user or not neo4j_password:
        logger.error("Neo4j credentials not provided. Please set NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD environment variables.")
        exit(1)
    
    if not qdrant_url:
        logger.error("Qdrant URL not provided. Please set QDRANT_URL environment variable.")
        exit(1)
    
    # Populate databases
    success = populate_medical_data(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        qdrant_url=qdrant_url,
        qdrant_api_key=qdrant_api_key
    )
    
    if success:
        logger.info("Medical data population completed successfully")
    else:
        logger.error("Medical data population failed") 