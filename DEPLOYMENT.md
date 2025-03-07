# Deployment Guide for Sage: Personal AI

This document provides instructions for deploying your Sage AI application to various hosting platforms.

## Prerequisites

- Git repository with your application code
- API keys for OpenAI and Anthropic
- Basic familiarity with command line tools

## Option 1: Streamlit Cloud (Recommended)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push
   ```

2. **Sign up for Streamlit Cloud**
   - Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account

3. **Deploy your app**
   - Click "New app"
   - Select your repository, branch, and main file (app.py)
   - Set environment variables:
     - OPENAI_API_KEY
     - ANTHROPIC_API_KEY
     - ALLOWED_USERS (JSON string of username:password pairs, e.g., `{"user1":"pass1","user2":"pass2"}`)
     - MAX_DAILY_CALLS (optional, default is 50)

4. **Access Control Settings**
   - Your app will be accessible only via direct link (not indexed by search engines)
   - The enhanced authentication system requires valid username/password
   - Usage quotas prevent excessive API usage
   - For additional privacy (paid plans only):
     - Go to your app settings in Streamlit Cloud
     - Enable "Private app" option
     - Add specific email addresses that can access the app

5. **Share with Intended Users**
   - Share the app URL only with intended users
   - Provide them with their username and password
   - Inform them about daily usage limits 