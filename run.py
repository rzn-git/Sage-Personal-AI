#!/usr/bin/env python3
"""
Run script for Sage: Personal AI
"""
import os
import subprocess
import sys

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import streamlit
        import openai
        import anthropic
        import dotenv
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("Warning: .env file not found.")
        print("Creating .env file from .env.example...")
        
        if os.path.exists(".env.example"):
            with open(".env.example", "r") as example_file:
                with open(".env", "w") as env_file:
                    env_file.write(example_file.read())
            print(".env file created. Please edit it to add your API keys.")
        else:
            print("Error: .env.example file not found.")
            print("Creating basic .env file...")
            with open(".env", "w") as env_file:
                env_file.write("OPENAI_API_KEY=your_openai_api_key_here\n")
                env_file.write("ANTHROPIC_API_KEY=your_anthropic_api_key_here\n")
            print(".env file created. Please edit it to add your API keys.")
        
        return False
    return True

def run_app():
    """Run the Streamlit app"""
    print("Starting Sage: Personal AI...")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    check_env_file()
    
    run_app() 