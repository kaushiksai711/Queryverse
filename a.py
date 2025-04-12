from hyperon import MeTTa

# Create a MeTTa instance first
metta = MeTTa()

# Create a space and bind it
metta.run('!(bind! &kb (new-space))')

try:
    # Load and run the knowledge base file
    with open('knowledge_base.metta', 'r') as f:
        kb_content = f.read()
        # Add content to the knowledge base
        result = metta.run(f'!(add-atom &kb {kb_content})')
        print("Knowledge base loaded:", result)

    # Try some queries
    print("\nQuerying the knowledge base:")
    
    # Query about diabetes
    result = metta.run('!(match &kb (is_a diabetes $X))')
    print("What is diabetes?:", result)
    
    # Query about treatments
    result = metta.run('!(match &kb (treats $X $Y))')
    print("Treatments:", result)
    
    # Query about symptoms
    result = metta.run('!(match &kb (symptom_of $X $Y))')
    print("Symptoms:", result)

except FileNotFoundError:
    print("Error: knowledge_base.metta file not found!")
except Exception as e:
    print(f"An error occurred: {str(e)}")















