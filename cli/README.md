# Medical FAQ Chatbot CLI

A command-line interface for interacting with the Medical FAQ Chatbot system.

## Features

- Interactive command-line interface
- Rich text formatting and progress indicators
- Support for medical queries
- Command shortcuts for common operations
- Markdown-formatted responses

## Installation

1. Make sure you have Python 3.8+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure your `.env` file is properly configured with database credentials

## Usage

Run the CLI interface:
```bash
python cli_interface.py
```

### Available Commands

- `/help` - Show help information
- `/exit` - Exit the program
- `/clear` - Clear the screen
- `/sources` - Show sources for the last response

### Example Queries

- What are the symptoms of diabetes?
- How is asthma treated?
- What causes high blood pressure?
- What is the difference between type 1 and type 2 diabetes?

## Configuration

The CLI uses the same environment variables as the main application. Make sure your `.env` file contains:

```
NEO4J_URI=your_neo4j_uri
NEO4J_USER=your_neo4j_user
NEO4J_PASSWORD=your_neo4j_password
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
MONGODB_URI=your_mongodb_uri
MONGODB_DB=your_mongodb_db
``` 