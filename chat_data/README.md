# Chat Data Directory

This directory stores user data and chat histories for the Sage AI application.

## Structure

- `users.json`: Contains user profiles and usage statistics
- `<username>/`: Individual user directories
  - `chats.json`: Chat history for each user

## Important Notes

1. The `users.json` file in this repository contains placeholder data for demonstration purposes only.
2. When deploying to Streamlit Cloud, user data will be stored in the `.streamlit` directory.
3. Real user data should never be committed to version control.
4. The `.gitignore` file is configured to exclude real user data from being committed.

## Security

For security reasons, the following files are excluded from version control:
- Real user chat histories
- Actual user credentials
- API keys and sensitive configuration

When deploying to Streamlit Cloud, make sure to configure proper authentication through the Streamlit secrets management system. 