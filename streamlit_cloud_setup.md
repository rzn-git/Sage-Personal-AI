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
- `ALLOWED_USERS`: JSON string of username:password pairs, e.g., `{"admin":"admin_password","user1":"password1"}`
- `MAX_DAILY_CALLS`: Maximum number of API calls allowed per day (default: 50)

## 4. Advanced Settings (Optional)

- **Secrets Management**: For more secure API key management, use Streamlit's secrets management
- **Custom Theme**: Customize the app appearance in the Streamlit Cloud settings
- **Access Control**: Set up access restrictions if needed

## 5. User Management

The application supports multiple users in two ways:

1. **Pre-defined users**: Set in the `ALLOWED_USERS` environment variable
2. **User signup**: Users can create their own accounts if enabled

Each user has:
- Their own chat history
- Individual usage tracking
- Personalized settings

## 6. API Key Management

There are two approaches for API key management:

1. **Admin-provided keys**: Set the API keys in environment variables
2. **User-provided keys**: Users can input their own API keys in the app

## 7. Troubleshooting

- **File Permissions**: Streamlit Cloud uses a read-only file system except for the `.streamlit` directory
- **Environment Variables**: Check that all required environment variables are set
- **Dependencies**: Ensure all dependencies are in requirements.txt with correct versions

## 8. Updating Your App

To update your app after making changes:

1. Commit and push changes to GitHub
2. Streamlit Cloud will automatically redeploy your app

## 9. Monitoring

- Monitor your app's usage in the Streamlit Cloud dashboard
- Check logs for any errors or issues 