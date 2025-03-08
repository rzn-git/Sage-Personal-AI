# Sage: Personal AI

A ChatGPT-like personal AI assistant built with Streamlit that maintains conversation context and allows model switching.

## Features

- Chat interface similar to ChatGPT
- Conversation context management
- Chat history sidebar
- Model selection (OpenAI and Anthropic models)
- New chat creation
- Pay-as-you-go pricing model with usage tracking
- User profiles with spending information
- Self-service user registration

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
   ALLOWED_USERS={"admin":"admin"}
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
2. Log in with existing credentials or sign up for a new account
3. Select a model from the dropdown
4. Start chatting!
5. Use the "New Chat" button to start a fresh conversation
6. Access previous conversations from the sidebar

## User Management

The application supports two ways to manage users:

1. **Admin-created users**: Add users to the `ALLOWED_USERS` environment variable in the `.env` file:
   ```
   ALLOWED_USERS={"admin":"admin","user1":"password1","user2":"password2"}
   ```

2. **Self-service registration**: Users can create their own accounts by clicking the "Sign Up" button on the login page. These user accounts are stored in the `chat_data/users.json` file.

Each user has their own:
- Profile with display name and optional profile picture
- Chat history
- Usage tracking and spending information

## Pay-as-you-go Pricing

The application includes a pay-as-you-go pricing model that tracks token usage and calculates costs based on the following rates (per million tokens):

| Model       | Input | Output |
|-------------|-------|--------|
| gpt-4o-mini | $0.15 | $0.60  |
| Claude 3.5  | $0.80 | $4.00  |
| o3-mini     | $1.10 | $4.40  |
| o1-mini     | $1.10 | $4.40  |
| gpt-4o      | $0.50 | $1.50  |
| Claude 3.7  | $3.00 | $15.00 |
| o1          | $15.00| $60.00 |

Each user's spending is tracked individually and displayed in the sidebar. Users can view detailed spending information by model in the "View Spending Details" section.

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