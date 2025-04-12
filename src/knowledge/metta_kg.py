import platform
import sys
import os

if platform.system() == 'Linux':
    from hyperon import MeTTa
else:
    print("Warning: MeTTa (hyperon) only works in Linux subsystem. Please run this code in WSL.")
    sys.exit(1)

from typing import List, Dict, Any, Optional

class MeTTaKnowledgeGraph:
    def __init__(self, kb_file: str = "knowledge_base.metta"):
        """Initialize MeTTa instance and load knowledge base."""
        self.metta = MeTTa()
        if os.path.exists(kb_file):
            self.load_knowledge_base(kb_file)
            
    def load_knowledge_base(self, kb_file: str):
        """Load knowledge base from a .metta file."""
        with open(kb_file, 'r') as f:
            kb_content = f.read()
        # Load the entire knowledge base at once
        self.metta.run(kb_content)
                
    def add_fact(self, subject: str, predicate: str, object_value: str):
        """Add a triple (fact) to the knowledge graph."""
        fact = f'!({predicate} "{subject}" "{object_value}")'
        self.metta.run(fact)
        
    def query(self, subject: Optional[str] = None, 
              predicate: Optional[str] = None,
              object_value: Optional[str] = None) -> List[Dict[str, str]]:
        """Query the knowledge graph with optional subject, predicate, object patterns."""
        # Direct fact query
        if subject and predicate and object_value:
            query = f'!({predicate} "{subject}" "{object_value}")'
            result = self.metta.run(query)
            if result:
                return [{
                    'predicate': predicate,
                    'subject': subject,
                    'object': object_value
                }]
            return []
            
        # Pattern matching query
        if predicate:
            p = predicate
        else:
            p = "$P"
            
        if subject:
            s = f'"{subject}"'
        else:
            s = "$S"
            
        if object_value:
            o = f'"{object_value}"'
        else:
            o = "$O"
            
        query = f'!(match &self ({p} {s} {o}))'
        results = self.metta.run(query)
        print(f"Query: {query}")
        print(f"Results: {results}")
        
        processed_results = []
        if results:
            for result in results:
                result_str = str(result)
                parts = result_str.strip('()').split()
                if len(parts) == 3:
                    processed_results.append({
                        'predicate': parts[0],
                        'subject': parts[1].strip('"'),
                        'object': parts[2].strip('"')
                    })
                    
        return processed_results

    def get_related_concepts(self, concept: str) -> List[Dict[str, str]]:
        """Get all concepts related to a given concept."""
        # Direct fact retrieval
        query = f'!({concept})'
        results = self.metta.run(query)
        print(f"Direct concept query: {query}")
        print(f"Results: {results}")
        
        processed_results = []
        if results:
            for result in results:
                result_str = str(result)
                if '(' in result_str and ')' in result_str:
                    parts = result_str.strip('()').split()
                    if len(parts) >= 3:
                        processed_results.append({
                            'predicate': parts[0],
                            'subject': parts[1].strip('"'),
                            'object': parts[2].strip('"')
                        })
                    
        return processed_results

    def get_specific_relations(self, relation_type: str, concept: str = None) -> List[Dict[str, str]]:
        """Get all facts with a specific relation type, optionally filtered by concept."""
        # Direct relation retrieval
        if concept:
            query = f'!({relation_type} $x "{concept}")'
        else:
            query = f'!({relation_type})'
            
        results = self.metta.run(query)
        print(f"Relation query: {query}")
        print(f"Results: {results}")
        
        processed_results = []
        if results:
            for result in results:
                result_str = str(result)
                if '(' in result_str and ')' in result_str:
                    parts = result_str.strip('()').split()
                    if len(parts) >= 3:
                        processed_results.append({
                            'predicate': parts[0],
                            'subject': parts[1].strip('"'),
                            'object': parts[2].strip('"')
                        })
                    
        return processed_results

    def add_hierarchical_relationship(self, parent: str, child: str, relationship_type: str = "is_a"):
        """Add hierarchical relationships to the knowledge graph."""
        self.add_fact(child, relationship_type, parent) 