# Deployment Guide for Sage: Personal AI

This document provides instructions for deploying your Sage AI application to various hosting platforms.

## Prerequisites

- Git repository with your application code
- API keys for OpenAI and Anthropic
- Basic familiarity with command line tools

## Option 1: Streamlit Cloud (Recommended for Simplicity)

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

## Option 2: Docker Deployment (Recommended for Security)

1. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your API keys and configuration to `.env`

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access your application**
   - Open http://localhost:8501 in your browser

4. **For production deployment**
   - Set up a reverse proxy (Nginx/Traefik) with HTTPS
   - Configure proper authentication
   - Consider using Docker Swarm or Kubernetes for scaling

## Option 3: Manual Deployment

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd sage-personal-ai
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your API keys to `.env`

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Security Best Practices

1. **API Key Protection**
   - Never commit API keys to version control
   - Use environment variables or a secrets manager
   - Rotate keys regularly

2. **Access Control**
   - Use the built-in authentication system
   - Set up HTTPS with a reverse proxy
   - Limit access to trusted users

3. **Usage Monitoring**
   - Monitor API usage to prevent unexpected costs
   - Set up alerts for unusual activity
   - Regularly review logs for security issues 