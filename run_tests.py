import os
import subprocess
import sys
from dotenv import load_dotenv

def download_spacy_model():
    """Download spaCy model with error handling"""
    try:
        print("Downloading spaCy model...")
        # First try to download the model
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
    except subprocess.CalledProcessError:
        print("Failed to download model using spacy download command. Trying alternative method...")
        try:
            # Try installing the model package directly
            subprocess.run([sys.executable, "-m", "pip", "install", "en-core-web-sm"], check=True)
            # Link the model
            subprocess.run([sys.executable, "-m", "spacy", "link", "en_core_web_sm", "en_core_web_sm", "--force"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading spaCy model: {str(e)}")
            print("\nPlease try downloading the model manually using:")
            print("python -m spacy download en_core_web_sm")
            sys.exit(1)

def download_nltk_data():
    """Download NLTK data"""
    try:
        print("Downloading NLTK data...")
        subprocess.run([sys.executable, "download_nltk_data.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading NLTK data: {str(e)}")
        print("\nPlease try downloading the NLTK data manually using:")
        print("python download_nltk_data.py")
        sys.exit(1)

def main():
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = [
        "NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD",
        "QDRANT_URL", "QDRANT_API_KEY",
        "MONGODB_URI", "MONGODB_DB"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file")
        return
    
    try:
        # Install the package in development mode
        print("Installing package in development mode...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], check=True)
        
        # Install test dependencies
        print("Installing test dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"], check=True)
        
        # Download spaCy model
        download_spacy_model()
        
        # Download NLTK data
        download_nltk_data()
        
        # Run tests
        print("\nRunning tests...")
        subprocess.run([sys.executable, "-m", "pytest", "tests/agents/test_backend.py", "-v"], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 