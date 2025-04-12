#!/usr/bin/env python
"""
Run script for the FAQ Chatbot system.

This script provides an easy way to run either the API server
or the demo with mock components.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

def run_api():
    """Run the FastAPI server."""
    import uvicorn
    from src.api.main import app
    
    print("Starting API server...")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

def run_demo():
    """Run the demo with mock components."""
    from src.main import main
    
    print("Running demo with mock components...")
    main()

def run_tests():
    """Run the test suite."""
    import pytest
    
    print("Running tests...")
    pytest.main(["-v", "tests/"])

def run_cli():
    """Run the CLI interface."""
    from cli.cli_interface import main as cli_main
    
    print("Starting CLI interface...")
    cli_main()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Run the FAQ Chatbot system")
    
    parser.add_argument(
        "mode", 
        choices=["api", "demo", "test", "cli"],
        help="Run mode: 'api' to start the API server, 'demo' to run the demo, 'test' to run tests, 'cli' to run CLI"
    )
    
    args = parser.parse_args()
    
    # Make sure we can import from src
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run in the specified mode
    if args.mode == "api":
        run_api()
    elif args.mode == "demo":
        run_demo()
    elif args.mode == "test":
        run_tests()
    elif args.mode == "cli":
        run_cli() 