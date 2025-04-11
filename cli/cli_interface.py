"""
Command Line Interface for the Medical FAQ Chatbot.

This module provides an interactive CLI for users to interact with the chatbot system.
"""

import os
import sys
import asyncio
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from dotenv import load_dotenv

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator import Orchestrator
from src.agents.query_interpreter import QueryInterpreter
from src.agents.query_decomposer import QueryDecomposer
from src.agents.retrieval_agent import RetrievalAgent
from src.db.neo4j_connector import Neo4jConnector
from src.db.qdrant_connector import QdrantConnector
from src.db.mongodb_connector import MongoDBConnector
from src.utils.logger import setup_logger

# Initialize rich console
console = Console()

class CLIInterface:
    """
    Command Line Interface for interacting with the chatbot system.
    """
    
    def __init__(self):
        """Initialize the CLI interface."""
        load_dotenv()
        self.logger = setup_logger("cli_interface")
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize all required components."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Initializing components...", total=None)
            
            # Initialize database connectors
            self.neo4j = Neo4jConnector(
                uri=os.getenv("NEO4J_URI"),
                user=os.getenv("NEO4J_USER"),
                password=os.getenv("NEO4J_PASSWORD")
            )
            
            self.qdrant = QdrantConnector(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY")
            )
            
            self.mongodb = MongoDBConnector(
                uri=os.getenv("MONGODB_URI"),
                db_name=os.getenv("MONGODB_DB")
            )
            
            # Connect to databases
            self.neo4j.connect()
            self.qdrant.connect()
            self.mongodb.connect()
            
            # Initialize agents
            self.query_interpreter = QueryInterpreter()
            self.query_decomposer = QueryDecomposer(self.query_interpreter)
            self.retrieval_agent = RetrievalAgent(self.neo4j, self.qdrant, self.mongodb)
            self.orchestrator = Orchestrator(
                self.query_interpreter,
                self.query_decomposer,
                self.retrieval_agent
            )
    
    async def process_query(self, query: str) -> Optional[str]:
        """
        Process a user query and return the response.
        
        Args:
            query: The user's query string
            
        Returns:
            The system's response or None if there was an error
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                progress.add_task(description="Processing your query...", total=None)
                
                # Process the query through the orchestrator
                result = await self.orchestrator.process_query(query)
                
                # Format the response
                if result and "response" in result:
                    response = result["response"]
                    if "sources" in result and result["sources"]:
                        response += "\n\nSources:\n"
                        for source in result["sources"]:
                            response += f"- {source}\n"
                    return response
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return None
    
    def display_help(self):
        """Display help information."""
        help_text = """
        Medical FAQ Chatbot CLI
        
        Commands:
        /help     - Show this help message
        /exit     - Exit the program
        /clear    - Clear the screen
        /sources  - Show sources for the last response
        
        Type your medical questions directly to get answers.
        Example questions:
        - What are the symptoms of diabetes?
        - How is asthma treated?
        - What causes high blood pressure?
        """
        console.print(Panel(help_text, title="Help", border_style="blue"))
    
    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
        Welcome to the Medical FAQ Chatbot!
        
        This CLI allows you to ask medical questions and get accurate,
        well-sourced answers. Type /help for available commands.
        """
        console.print(Panel(welcome_text, title="Medical FAQ Chatbot", border_style="green"))
    
    async def run(self):
        """Run the CLI interface."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                query = Prompt.ask("\n[bold blue]You[/bold blue]")
                
                # Handle commands
                if query.lower() == "/exit":
                    console.print("[bold green]Goodbye![/bold green]")
                    break
                elif query.lower() == "/help":
                    self.display_help()
                    continue
                elif query.lower() == "/clear":
                    console.clear()
                    continue
                
                # Process the query
                response = await self.process_query(query)
                
                if response:
                    # Display the response
                    console.print("\n[bold green]Chatbot[/bold green]")
                    console.print(Markdown(response))
                else:
                    console.print("[bold red]Sorry, I couldn't process your query. Please try again.[/bold red]")
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow]Use /exit to quit the program[/bold yellow]")
            except Exception as e:
                self.logger.error(f"Error in CLI: {str(e)}")
                console.print(f"[bold red]An error occurred: {str(e)}[/bold red]")

def main():
    """Main entry point for the CLI."""
    cli = CLIInterface()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main() 