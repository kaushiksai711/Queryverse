from typing import List, Dict, Any, Optional
from src.knowledge.metta_kg import MeTTaKnowledgeGraph
import re

class MeTTaFAQChatbot:
    def __init__(self):
        """Initialize the FAQ chatbot with MeTTa knowledge graph."""
        self.kg = MeTTaKnowledgeGraph()
        self.initialize_knowledge_base()
        
    def initialize_knowledge_base(self):
        """Initialize the knowledge base with domain-specific knowledge."""
        # Example: Adding some medical domain knowledge
        # This should be replaced with your specific domain knowledge
        
        # Add basic facts
        self.kg.add_fact("diabetes", "is_a", "medical_condition")
        self.kg.add_fact("insulin", "treats", "diabetes")
        self.kg.add_fact("blood_sugar", "symptom_of", "diabetes")
        
        # Add hierarchical relationships
        self.kg.add_hierarchical_relationship("medical_condition", "chronic_disease")
        self.kg.add_hierarchical_relationship("chronic_disease", "diabetes")
        
        # Add rules
        self.kg.add_rule(
            "requires_monitoring",
            [("X", "is_a", "chronic_disease")]
        )
        
    def process_question(self, question: str) -> dict:
        """Process user question and generate response using knowledge graph."""
        # Extract key concepts and relation type from question
        concepts, relation_type = self._analyze_question(question)
        
        # Get relevant facts based on question type
        facts = []
        if relation_type:
            for concept in concepts:
                facts.extend(self.kg.get_specific_relations(relation_type, concept))
        else:
            for concept in concepts:
                facts.extend(self.kg.get_related_concepts(concept))
                
        # Generate response
        response = self._generate_response(question, facts)
        
        return {
            "question": question,
            "response": response,
            "related_facts": facts,
            "concepts_identified": concepts
        }
        
    def _analyze_question(self, question: str) -> tuple:
        """
        Analyze question to extract concepts and determine relation type.
        Returns tuple of (concepts, relation_type)
        """
        question = question.lower()
        concepts = []
        relation_type = None
        
        # Map question patterns to relation types
        if "treat" in question or "treatment" in question:
            relation_type = "treats"
        elif "symptom" in question:
            relation_type = "symptom_of"
        elif "cause" in question or "complication" in question:
            relation_type = "can_cause"
        elif "risk" in question:
            relation_type = "risk_factor"
        elif "what is" in question:
            relation_type = "is_a"
            
        # Extract concepts
        words = question.split()
        for word in words:
            # Query both as subject and object to see if word is a known concept
            if self.kg.get_related_concepts(word):
                concepts.append(word)
                
        return concepts, relation_type
        
    def _generate_response(self, question: str, facts: list) -> str:
        """Generate natural language response using retrieved facts."""
        if not facts:
            return "I don't have enough information to answer that question."
            
        # Group facts by relation type for better organization
        facts_by_relation = {}
        for fact in facts:
            relation = fact['predicate']
            if relation not in facts_by_relation:
                facts_by_relation[relation] = []
            facts_by_relation[relation].append(fact)
            
        # Generate response parts for each relation type
        response_parts = ["Based on my knowledge:"]
        
        for relation, related_facts in facts_by_relation.items():
            # Format based on relation type
            if relation == "is_a":
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} is a {fact['object']}")
            elif relation == "treats":
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} can treat {fact['object']}")
            elif relation == "symptom_of":
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} is a symptom of {fact['object']}")
            elif relation == "can_cause":
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} can cause {fact['object']}")
            elif relation == "risk_factor":
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} is a risk factor for {fact['object']}")
            else:
                for fact in related_facts:
                    response_parts.append(f"- {fact['subject']} {relation} {fact['object']}")
                    
        return "\n".join(response_parts)
        
    def add_knowledge(self, subject: str, predicate: str, object_value: str):
        """
        Add new knowledge to the graph.
        
        Args:
            subject: Subject of the fact
            predicate: Relationship/predicate
            object_value: Object/value
        """
        self.kg.add_fact(subject, predicate, object_value)
        
    def learn_from_interaction(self, question: str, correct_answer: str):
        """
        Learn from user interactions to improve knowledge base.
        
        Args:
            question: User's question
            correct_answer: Correct answer provided by user/expert
        """
        concepts = self._extract_concepts(question)
        if concepts:
            q_id = f"q_{hash(question)}"
            self.kg.add_fact(q_id, "question_text", question)
            self.kg.add_fact(q_id, "answer_text", correct_answer)
            for concept in concepts:
                self.kg.add_fact(q_id, "relates_to", concept) 