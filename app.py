"""
Sage: Personal AI - A secure, customizable personal AI assistant
"""
import os
import streamlit as st

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Sage: Personal AI",
    page_icon="🔆",
    layout="wide",
    initial_sidebar_state="expanded"
)

import uuid
import datetime
import json
import logging
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from error_handler import handle_error, api_error_handler, APIError, ModelNotAvailableError
from utils import (
    num_tokens_from_string, 
    calculate_cost, 
    save_chats, 
    load_chats, 
    update_user_spending,
    format_timestamp,
    format_currency
)

# Configure logging
from logging_config import setup_logging
setup_logging()
logger = logging.getLogger("personal_chatbot")

# Load environment variables
load_dotenv()

# Get API keys from Streamlit secrets or environment variables
try:
    # Try to get API keys from Streamlit secrets first
    if "api_keys" in st.secrets:
        openai_api_key = st.secrets["api_keys"].get("openai")
        anthropic_api_key = st.secrets["api_keys"].get("anthropic")
    else:
        # Fall back to environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key:
        st.warning("OpenAI API key not found. Some models may not be available.")
        # For Streamlit Cloud, provide a way for users to input their own API key
        if "openai_api_key" not in st.session_state:
            st.session_state.openai_api_key = ""
        
        # Only show this input if user is authenticated
        if st.session_state.get("authenticated", False):
            with st.sidebar.expander("OpenAI API Key"):
                openai_api_key = st.text_input(
                    "Enter your OpenAI API key:", 
                    value=st.session_state.openai_api_key,
                    type="password",
                    key="openai_api_key_input"
                )
                st.session_state.openai_api_key = openai_api_key
    
    if not anthropic_api_key:
        st.warning("Anthropic API key not found. Some models may not be available.")
        # For Streamlit Cloud, provide a way for users to input their own API key
        if "anthropic_api_key" not in st.session_state:
            st.session_state.anthropic_api_key = ""
        
        # Only show this input if user is authenticated
        if st.session_state.get("authenticated", False):
            with st.sidebar.expander("Anthropic API Key"):
                anthropic_api_key = st.text_input(
                    "Enter your Anthropic API key:", 
                    value=st.session_state.anthropic_api_key,
                    type="password",
                    key="anthropic_api_key_input"
                )
                st.session_state.anthropic_api_key = anthropic_api_key
    
    # Use session state API keys if available
    if not openai_api_key and st.session_state.get("openai_api_key"):
        openai_api_key = st.session_state.openai_api_key
    
    if not anthropic_api_key and st.session_state.get("anthropic_api_key"):
        anthropic_api_key = st.session_state.anthropic_api_key
    
    # Initialize API clients without any extra parameters
    openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
    anthropic_client = Anthropic(api_key=anthropic_api_key) if anthropic_api_key else None
except Exception as e:
    st.error(f"Error initializing API clients: {str(e)}")

# Import authentication
try:
    from auth_config import check_password, set_usage_quota, get_profile_picture_html, update_user_profile, set_signup_mode
    auth_enabled = True
except ImportError:
    auth_enabled = False
    def set_usage_quota():
        return True
    def get_profile_picture_html():
        return ""
    def update_user_profile():
        return True
    def set_signup_mode(enabled):
        return True

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 2.5em;
        background-color: #f0f2f6;
        border: none;
        margin-bottom: 5px;
    }
    .stButton button:hover {
        background-color: #e0e2e6;
    }
    .user-info {
        display: flex;
        align-items: center;
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .user-avatar {
        margin-right: 15px;
    }
    .user-details {
        flex-grow: 1;
    }
    .user-name {
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 5px;
    }
    .user-spending {
        color: #555;
        font-size: 0.9em;
    }
    .spending-details {
        margin-top: 10px;
        padding: 10px;
        background-color: #f5f5f5;
        border-radius: 5px;
        font-size: 0.9em;
    }
    .new-chat-button {
        margin-bottom: 15px;
    }
    .sidebar-footer {
        position: absolute;
        bottom: 80px;
        width: calc(100% - 40px);
        padding: 0 20px;
    }
    .settings-button {
        position: absolute;
        bottom: 20px;
        width: calc(100% - 40px);
        padding: 0 20px;
    }
    .settings-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }
    .settings-field {
        margin-bottom: 15px;
    }
    .refresh-button {
        text-align: center;
        margin-bottom: 15px;
        margin-top: 5px;
    }
    .refresh-button button {
        padding: 0.25rem 0.75rem;
        font-size: 0.9rem;
        line-height: 1.2;
        border-radius: 0.25rem;
        height: auto;
        display: inline-block;
        width: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Function to get user-specific chat file path
def get_user_chat_file(username):
    """Get the chat file path for a specific user"""
    import os
    from utils import CHAT_DATA_DIR
    # Create user-specific directory if it doesn't exist
    user_dir = os.path.join(CHAT_DATA_DIR, username)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    return os.path.join(user_dir, "chats.json")

# Function to load user-specific chats
def load_user_chats(username):
    """Load chats for a specific user"""
    import json
    chat_file = get_user_chat_file(username)
    if not os.path.exists(chat_file):
        return {}
    
    try:
        with open(chat_file, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty dict if file is corrupted or doesn't exist
        return {}

# Function to save user-specific chats
def save_user_chats(username, chats):
    """Save chats for a specific user"""
    import json
    chat_file = get_user_chat_file(username)
    with open(chat_file, 'w') as f:
        json.dump(chats, f, indent=2)

# Function to refresh user spending data
def refresh_spending_data():
    """Refresh the user's spending data from the database"""
    if not st.session_state.get("authenticated", False):
        return
    
    username = st.session_state.get("current_user")
    if not username:
        return
    
    # Load fresh user data
    user_data = load_user_data()
    if username in user_data:
        # Update session state with fresh data
        st.session_state["user_profile"] = user_data[username]
        # Set a flag to show a success message
        st.session_state["refresh_success"] = True

# Initialize session state
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo"

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

if "refresh_success" not in st.session_state:
    st.session_state.refresh_success = False

# Initialize chat-related session state variables
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Define available models
MODELS = {
    "gpt-4o-mini": {"provider": "openai", "name": "gpt-4o-mini"},
    "claude-3-5-haiku-20241022": {"provider": "anthropic", "name": "claude-3-5-haiku-20241022"},
    "o3-mini": {"provider": "openai", "name": "o3-mini"},
    "o1-mini": {"provider": "openai", "name": "o1-mini"},
    "gpt-4o": {"provider": "openai", "name": "gpt-4o"},
    "claude-3-7-sonnet-20250219": {"provider": "anthropic", "name": "claude-3-7-sonnet-20250219"},
    "o1": {"provider": "openai", "name": "o1"}
}

# Function to toggle settings
def toggle_settings():
    st.session_state.show_settings = not st.session_state.show_settings

# Function to update user settings
def update_settings():
    if not st.session_state.get("authenticated", False):
        return
    
    username = st.session_state.get("current_user")
    if not username:
        return
    
    # Get values from session state
    new_password = st.session_state.get("new_password", "")
    confirm_password = st.session_state.get("confirm_password", "")
    
    # Validate inputs
    if new_password and new_password != confirm_password:
        st.session_state["settings_error"] = "Passwords do not match"
        return
    
    # Update user data
    from utils import load_user_data, save_user_data
    user_data = load_user_data()
    
    if username in user_data:
        # Update password if provided
        if new_password:
            user_data[username]["password"] = new_password
        
        # Save updated user data
        save_user_data(user_data)
        st.session_state["settings_success"] = True

# Function to create a new chat - moved up before it's called
@handle_error
def create_new_chat():
    # Check usage quota
    if not set_usage_quota():
        return None
    
    # Get current username
    username = st.session_state.get("current_user")
    if not username:
        return None
    
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.datetime.now().isoformat(),
        "model": st.session_state.model,
        "user": username  # Add user ownership to the chat
    }
    st.session_state.current_chat_id = chat_id
    
    # Save user-specific chats
    save_user_chats(username, st.session_state.chats)
    return chat_id

# Function to get chat response from OpenAI
@api_error_handler("openai")
def get_openai_response(messages, model):
    # Check if OpenAI client is initialized
    if openai_client is None:
        raise APIError("OpenAI API key not configured. Please add your API key in the sidebar.")
        
    # Track API usage
    username = st.session_state.get("current_user", "anonymous")
    
    # Convert messages to OpenAI format
    formatted_messages = []
    input_tokens = 0
    
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
        input_tokens += num_tokens_from_string(msg["content"], model)
    
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            temperature=0.7,
        )
        
        content = response.choices[0].message.content
        output_tokens = num_tokens_from_string(content, model)
        
        # Update user spending
        update_user_spending(username, model, input_tokens, output_tokens)
        
        return content
    except Exception as e:
        raise APIError(f"OpenAI API error: {str(e)}")

# Function to get chat response from Anthropic
@api_error_handler("anthropic")
def get_anthropic_response(messages, model):
    # Check if Anthropic client is initialized
    if anthropic_client is None:
        raise APIError("Anthropic API key not configured. Please add your API key in the sidebar.")
        
    # Track API usage
    username = st.session_state.get("current_user", "anonymous")
    
    # Convert messages to Anthropic format
    system_prompt = ""
    formatted_messages = []
    input_tokens = 0
    
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"]
            input_tokens += num_tokens_from_string(msg["content"], model)
        else:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
            input_tokens += num_tokens_from_string(msg["content"], model)
    
    try:
        response = anthropic_client.messages.create(
            model=model,
            system=system_prompt,
            messages=formatted_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        content = response.content[0].text
        output_tokens = num_tokens_from_string(content, model)
        
        # Update user spending
        update_user_spending(username, model, input_tokens, output_tokens)
        
        return content
    except Exception as e:
        raise APIError(f"Anthropic API error: {str(e)}")

# Function to get chat response
@handle_error
def get_chat_response(messages, model_info):
    """Get response from the selected model"""
    model = model_info["name"]  # Use "name" instead of "id"
    provider = model_info["provider"]
    
    # Check if we have the necessary API key
    if provider == "openai" and openai_client is None:
        st.error("OpenAI API key not configured. Please add your API key in the sidebar.")
        return None
    
    if provider == "anthropic" and anthropic_client is None:
        st.error("Anthropic API key not configured. Please add your API key in the sidebar.")
        return None
    
    # Get response based on provider
    if provider == "openai":
        return get_openai_response(messages, model)
    elif provider == "anthropic":
        return get_anthropic_response(messages, model)
    else:
        raise ModelNotAvailableError(f"Provider {provider} not supported")

# Main chat interface
if auth_enabled:
    # Initialize signup mode if not already set
    if "signup_mode" not in st.session_state:
        st.session_state["signup_mode"] = False
        
    # Check if the user is authenticated
    if not st.session_state.get("authenticated", False):
        # Check if we're in signup mode
        if st.session_state.get("signup_mode", False):
            # The signup form will be shown by check_password()
            check_password()
            # Stop execution after showing signup form
            st.stop()
        
        # Show login form
        st.title("🔆 Sage: Personal AI")
        
        # Create columns for login form
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Login")
            
            # Username input
            st.text_input("Username", key="app_username")
            
            # Password input
            st.text_input("Password", type="password", key="app_password")
            
            # Login button
            if st.button("Login", key="app_login_button"):
                # Add debugging
                st.write(f"DEBUG - Login button clicked")
                st.write(f"DEBUG - app_username: {st.session_state.get('app_username', 'not set')}")
                st.write(f"DEBUG - app_password: {'*****' if 'app_password' in st.session_state else 'not set'}")
                
                # Copy values to the keys expected by auth_config.py
                if "app_username" in st.session_state and "app_password" in st.session_state:
                    st.session_state["auth_username"] = st.session_state["app_username"]
                    st.session_state["auth_password"] = st.session_state["app_password"]
                    
                    # Add debugging
                    st.write(f"DEBUG - Copied credentials to auth_username and auth_password")
                
                if not check_password():
                    st.error("Invalid username or password")
                    # Add debugging
                    st.write(f"DEBUG - check_password() returned False")
            
            # Toggle signup mode
            def enable_signup_mode():
                st.session_state["signup_mode"] = True
                
            if st.button("Sign Up", on_click=enable_signup_mode, key="app_signup_button"):
                st.rerun()
        
        with col2:
            st.image("https://img.freepik.com/free-vector/ai-technology-brain-background-smart-digital-transformation_53876-124672.jpg", 
                    use_container_width=True)
            
            st.markdown("""
            ### Welcome to Sage AI
            
            Your personal AI assistant powered by:
            - OpenAI GPT models
            - Anthropic Claude models
            
            Securely chat with advanced AI models and keep track of your conversations.
            """)
        
        # Show features
        st.markdown("---")
        st.subheader("Features")
        
        feature_col1, feature_col2, feature_col3 = st.columns(3)
        
        with feature_col1:
            st.markdown("### 🔒 Secure")
            st.markdown("User authentication and data protection")
        
        with feature_col2:
            st.markdown("### 💬 Multiple Models")
            st.markdown("Choose from various AI models")
        
        with feature_col3:
            st.markdown("### 📊 Usage Tracking")
            st.markdown("Monitor your API usage and costs")
        
        # Show footer
        st.markdown("---")
        st.markdown("© 2025 Sage AI. All rights reserved.")
        
        # Exit early if not authenticated
        st.stop()
    
    # If we get here, user is authenticated
    username = st.session_state.get("current_user", "Guest")
    
    # Load user's chats
    if username and username != "Guest":
        user_chats = load_user_chats(username)
        if user_chats:
            st.session_state.chats = user_chats
else:
    # No authentication, set default username
    username = "Guest"
    st.session_state["authenticated"] = True
    st.session_state["current_user"] = username

if st.session_state.current_chat_id is None or st.session_state.current_chat_id not in st.session_state.chats:
    create_new_chat()

current_chat = st.session_state.chats[st.session_state.current_chat_id]

# Display chat title with a modern look
st.markdown(f"<h2 style='color: black;'>{current_chat['title']}</h2>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0.5rem 0 1.5rem 0; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# Create a container for the chat messages
chat_container = st.container()
with chat_container:
    # Display chat messages
    for message in current_chat["messages"]:
        role_class = message["role"]  # 'user' or 'assistant'
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🔆"):
            st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat
    current_chat["messages"].append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Get AI response
    with st.chat_message("assistant", avatar="🔆"):
        with st.spinner("Thinking..."):
            messages_for_api = [{"role": m["role"], "content": m["content"]} for m in current_chat["messages"]]
            response = get_chat_response(messages_for_api, MODELS[st.session_state.model])
            st.markdown(response)
    
    # Add assistant response to chat
    current_chat["messages"].append({"role": "assistant", "content": response})
    
    # Update chat title if it's the first message
    if len(current_chat["messages"]) == 2:  # After first exchange (user + assistant)
        current_chat["title"] = get_chat_title_from_content(current_chat["messages"][0]["content"])
    
    # Save chats to disk - use user-specific save function
    username = st.session_state.get("current_user")
    if username:
        save_user_chats(username, st.session_state.chats)
    else:
        save_chats(st.session_state.chats)  # Fallback to global save


