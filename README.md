# Sage: Personal AI Assistant

A powerful AI chat assistant built with Streamlit that supports both OpenAI and Anthropic models.

## Features

- Multi-model support (OpenAI GPT models and Anthropic Claude models)
- User authentication system
- Chat history management
- Usage tracking and spending analytics
- Responsive UI with dark/light mode
- API key management

## Deployment to Streamlit Cloud

### 1. Fork or Clone this Repository

First, fork or clone this repository to your GitHub account.

### 2. Set Up Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select this repository, branch (main), and the main file (app.py)

### 3. Configure Environment Variables

In the Streamlit Cloud deployment settings, add the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (optional if users will provide their own)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional if users will provide their own)
- `ALLOWED_USERS`: JSON string of username:password pairs, e.g., `{"admin":"admin_password","user1":"password1"}`
- `MAX_DAILY_CALLS`: Maximum number of API calls allowed per day (default: 50)

### 4. Deploy

Click "Deploy" and your app will be live on Streamlit Cloud!

### 5. User Management

- The app supports multiple users as defined in the `ALLOWED_USERS` environment variable
- Each user has their own chat history and usage tracking
- Users can also sign up if enabled in the app

## Local Development

### Prerequisites

- Python 3.8+
- OpenAI API key
- Anthropic API key (optional)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/sage-personal-ai.git
cd sage-personal-ai
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
ALLOWED_USERS={"admin":"admin_password"}
```

4. Run the app
```bash
streamlit run app.py
```

## Project Structure

```
sage-personal-ai/
├── app.py              # Main Streamlit application
├── auth_config.py      # Authentication configuration
├── error_handler.py    # Error handling utilities
├── logging_config.py   # Logging configuration
├── utils.py            # Utility functions
├── requirements.txt    # Python dependencies
└── chat_data/          # Directory for user data and chat history
    └── users.json      # User profiles and usage data
```

## License

MIT

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Uses [OpenAI API](https://openai.com/api/) and [Anthropic API](https://anthropic.com/) 