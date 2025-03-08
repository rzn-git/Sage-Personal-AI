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

For detailed deployment instructions, see [streamlit_cloud_setup.md](streamlit_cloud_setup.md).

### Quick Start

1. Fork or clone this repository to your GitHub account
2. Sign up for [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy your app by connecting to your GitHub repository
4. Configure environment variables or secrets for authentication and API keys

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
ALLOWED_USERS={"admin":"your_secure_password"}
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
├── .env.example        # Example environment variables
├── streamlit_cloud_setup.md  # Streamlit Cloud deployment guide
└── chat_data/          # Directory for user data and chat history
    ├── README.md       # Information about the chat data directory
    ├── users.json      # User profiles and usage data (example)
    ├── admin/          # Example admin user directory
    ├── user1/          # Example user1 directory
    └── user2/          # Example user2 directory
```

## License

MIT

## Acknowledgements

- Built with [Streamlit](https://streamlit.io/)
- Uses [OpenAI API](https://openai.com/api/) and [Anthropic API](https://anthropic.com/) 