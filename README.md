# Sage: Personal AI

A ChatGPT-like personal AI assistant built with Streamlit that maintains conversation context and allows model switching.

## Features

- Chat interface similar to ChatGPT
- Conversation context management
- Chat history sidebar
- Model selection (OpenAI and Anthropic models)
- New chat creation

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

1. Run the application:
   ```
   streamlit run app.py
   ```
   Or use the provided scripts:
   ```
   # Windows
   run.bat
   
   # Linux/Mac
   ./run.sh
   ```
2. Select a model from the dropdown
3. Start chatting!
4. Use the "New Chat" button to start a fresh conversation
5. Access previous conversations from the sidebar

## Available Models

- OpenAI o1
- OpenAI o1-mini
- OpenAI o3-mini
- OpenAI gpt-4o
- OpenAI gpt-4o-mini
- Anthropic claude-3-7-sonnet-20250219
- Anthropic claude-3-5-haiku-20241022
- Anthropic claude-3-5-sonnet-20241022

## Development

- Run tests: `python -m unittest test_app.py`
- Clean up: `make clean`
- Create virtual environment: `make venv` 