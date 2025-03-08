# Streamlit Cloud Deployment Guide

This guide provides step-by-step instructions for deploying Sage Personal AI to Streamlit Cloud.

## 1. Prepare Your Repository

1. Make sure your repository is public on GitHub
2. Ensure all necessary files are committed:
   - app.py (main application)
   - requirements.txt (dependencies)
   - chat_data/users.json (user data)
   - All other Python modules

## 2. Set Up Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch (main), and the main file (app.py)

## 3. Configure Environment Variables

In the Streamlit Cloud deployment settings, add the following environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key (optional if users will provide their own)
- `ANTHROPIC_API_KEY`: Your Anthropic API key (optional if users will provide their own)
- `ALLOWED_USERS`: JSON string of username:password pairs, e.g., `{"username1":"password1","username2":"password2"}`
- `MAX_DAILY_CALLS`: Maximum number of API calls allowed per day (default: 50)

> **IMPORTANT SECURITY NOTE**: The `ALLOWED_USERS` environment variable contains sensitive login credentials. Make sure to:
> 1. Use strong, unique passwords
> 2. Never use default or easily guessable credentials
> 3. Consider using Streamlit's secrets management instead of environment variables for better security

## 4. Using Streamlit Secrets (Recommended)

For better security, use Streamlit's secrets management instead of environment variables:

1. In the Streamlit Cloud dashboard, go to your app settings
2. Find the "Secrets" section
3. Add the following secrets in TOML format:

```toml
[api_keys]
openai = "your_openai_api_key"
anthropic = "your_anthropic_api_key"

[auth]
# Replace with your actual usernames and secure passwords
allowed_users = """{"username1":"secure_password1","username2":"secure_password2"}"""
max_daily_calls = 50
```

Then modify your app.py to use secrets instead of environment variables:

```python
# At the top of your app.py file
import streamlit as st

# Access secrets
openai_api_key = st.secrets["api_keys"]["openai"] if "api_keys" in st.secrets else os.environ.get("OPENAI_API_KEY")
anthropic_api_key = st.secrets["api_keys"]["anthropic"] if "api_keys" in st.secrets else os.environ.get("ANTHROPIC_API_KEY")
allowed_users = st.secrets["auth"]["allowed_users"] if "auth" in st.secrets else os.environ.get("ALLOWED_USERS")
```

## 5. Advanced Settings (Optional)

- **Custom Theme**: Customize the app appearance in the Streamlit Cloud settings
- **Access Control**: Set up access restrictions if needed

## 6. User Management

The application supports multiple users in two ways:

1. **Pre-defined users**: Set in the `ALLOWED_USERS` environment variable or secrets
2. **User signup**: Users can create their own accounts if enabled

Each user has:
- Their own chat history
- Individual usage tracking
- Personalized settings

## 7. API Key Management

There are two approaches for API key management:

1. **Admin-provided keys**: Set the API keys in environment variables or secrets
2. **User-provided keys**: Users can input their own API keys in the app

## 8. Troubleshooting

- **File Permissions**: Streamlit Cloud uses a read-only file system except for the `.streamlit` directory
- **Environment Variables**: Check that all required environment variables are set
- **Dependencies**: Ensure all dependencies are in requirements.txt with correct versions

## 9. Updating Your App

To update your app after making changes:

1. Commit and push changes to GitHub
2. Streamlit Cloud will automatically redeploy your app

## 10. Monitoring

- Monitor your app's usage in the Streamlit Cloud dashboard
- Check logs for any errors or issues 