"""
Main application entry point for the MeTTa FAQ Chatbot demo.
"""

#from src.agents.metta_chatbot import MeTTaFAQChatbot

def main():
    """
    Main function to demonstrate the MeTTa FAQ Chatbot functionality.
    """
    print("Starting MeTTa FAQ Chatbot Demo")
    print("===============================")
    
    # Initialize the chatbot with the knowledge base file
    chatbot = MeTTaFAQChatbot()
    
    # Example queries to test the knowledge base
    questions = [
        "What is diabetes?",
        "How is type 2 diabetes treated?",
        "What are the symptoms of diabetes?",
        "What complications can diabetes cause?",
        "What are the risk factors for type 2 diabetes?"
    ]
    
    for question in questions:
        print(f"\nQ: {question}")
        response = chatbot.process_question(question)
        print(f"A: {response['response']}")
        print("\nIdentified concepts:", response['concepts_identified'])

if __name__ == "__main__":
    main() 