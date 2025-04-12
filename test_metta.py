from hyperon import MeTTa
from typing import List, Dict, Optional, Any, Tuple

# Initialize MeTTa
metta = MeTTa()

# Create a space and bind it
metta.run('!(bind! &kb (new-space))')

# Add our base facts - now adding them to the specific space
facts = [
    '!(add-atom &kb (is_a diabetes medical_condition))',
    '!(add-atom &kb (treats insulin diabetes))',
    '!(add-atom &kb (symptom_of increased_thirst diabetes))',
    '!(add-atom &kb (is_a type_2_diabetes diabetes))',
    '!(add-atom &kb (treats metformin type_2_diabetes))',
    '!(add-atom &kb (symptom_of frequent_urination diabetes))',
    '!(add-atom &kb (risk_factor obesity type_2_diabetes))'
]

for f in facts:
    metta.run(f)

# Get all atoms in the knowledge base
all_atoms_result = metta.run('!(get-atoms &kb)')
print("\nRaw atoms result:")
print(all_atoms_result)

# Function to extract atoms from the nested structure
def extract_atoms(atoms_result):
    """Extract atoms from the MeTTa result structure."""
    extracted = []
    
    if isinstance(atoms_result, list) and len(atoms_result) > 0:
        # The first level is a list containing all atoms
        for atom in atoms_result[0]:  # Take the first element which contains our atoms
            # Each atom is a string like "(predicate subject object)"
            # Convert the atom to a more usable format
            atom_str = str(atom)
            # Remove outer parentheses and split
            parts = atom_str.strip('()').split()
            if len(parts) == 3:
                extracted.append(tuple(parts))
    
    return extracted

# Function to parse atom (simplified as we now have clean tuples)
def parse_atom(atom):
    """Parse an atom into (predicate, subject, object) format."""
    if isinstance(atom, tuple) and len(atom) == 3:
        return atom
    return None

# Function to filter atoms based on subject, predicate, object
def filter_atoms(atoms, subject=None, predicate=None, object_value=None):
    """Filter atoms based on subject, predicate, object patterns."""
    results = []
    
    for atom in atoms:
        parsed = parse_atom(atom)
        if parsed:
            pred, subj, obj = parsed
            
            # Check if it matches the filter criteria
            subj_match = subject is None or subj == subject
            pred_match = predicate is None or pred == predicate
            obj_match = object_value is None or obj == object_value
            
            if subj_match and pred_match and obj_match:
                results.append(parsed)
    
    return results

# Extract the actual atoms
all_atoms = extract_atoms(all_atoms_result)
print(f"\nExtracted atoms: {all_atoms}")

# Now we can perform our queries
print("\nQuerying all facts about diabetes:")
diabetes_facts = filter_atoms(all_atoms, subject="diabetes")
print(f"Facts about diabetes: {diabetes_facts}")

print("\nQuerying all facts where diabetes is the object:")
diabetes_obj_facts = filter_atoms(all_atoms, object_value="diabetes")
print(f"Facts where diabetes is object: {diabetes_obj_facts}")

print("\nQuerying all treatments:")
treatment_facts = filter_atoms(all_atoms, predicate="treats")
print(f"All treatments: {treatment_facts}")

class MeTTaKnowledgeGraph:
    def __init__(self, metta: MeTTa):
        self.metta = metta
        # Initialize the knowledge base space
        self.metta.run('!(bind! &kb (new-space))')

    def add_fact(self, predicate: str, subject: str, object_value: str) -> Any:
        """Add a fact to the knowledge graph."""
        cmd = f'!(add-atom &kb ({predicate} {subject} {object_value}))'
        return self.metta.run(cmd)

    def get_all_atoms(self) -> List:
        """Get all atoms in the knowledge base."""
        raw_result = self.metta.run('!(get-atoms &kb)')
        return extract_atoms(raw_result)

    def query(self, subject: Optional[str] = None, 
              predicate: Optional[str] = None,
              object_value: Optional[str] = None) -> List[Tuple[str, str, str]]:
        """Query the knowledge graph with optional subject, predicate, object patterns."""
        all_atoms = self.get_all_atoms()
        return filter_atoms(all_atoms, subject, predicate, object_value)

# Example usage
if __name__ == "__main__":
    print("\n--- Testing Knowledge Graph Class ---")
    kg = MeTTaKnowledgeGraph(MeTTa())
    
    # Add some facts
    kg.add_fact("is_a", "diabetes", "medical_condition")
    kg.add_fact("treats", "insulin", "diabetes")
    kg.add_fact("symptom_of", "increased_thirst", "diabetes")
    
    # Get all atoms to verify they were added
    print("\nAll atoms in knowledge base:")
    all_atoms = kg.get_all_atoms()
    print(f"Atoms: {all_atoms}")
    
    # Query examples
    print("\nClass-based queries:")
    all_facts = kg.query()
    print(f"All facts: {all_facts}")
    
    diabetes_facts = kg.query(subject="diabetes")
    print(f"Facts about diabetes: {diabetes_facts}")
    
    treatment_facts = kg.query(predicate="treats")
    print(f"Treatment relationships: {treatment_facts}")