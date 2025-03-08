import streamlit as st
import uuid
import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from utils import (
    save_chats, 
    load_chats, 
    get_chat_title_from_content, 
    format_timestamp, 
    num_tokens_from_string, 
    update_user_spending,
    format_currency,
    load_user_data
)
from error_handler import handle_error, api_error_handler, APIError, ModelNotAvailableError

# Load environment variables
load_dotenv()

# Initialize API clients
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key:
        st.warning("OpenAI API key not found. Some models may not be available.")
    
    if not anthropic_api_key:
        st.warning("Anthropic API key not found. Some models may not be available.")
    
    openai_client = OpenAI(api_key=openai_api_key)
    anthropic_client = Anthropic(api_key=anthropic_api_key)
except Exception as e:
    st.error(f"Error initializing API clients: {str(e)}")

# Import authentication
try:
    from auth_config import check_password, set_usage_quota, get_profile_picture_html, update_user_profile
    auth_enabled = True
except ImportError:
    auth_enabled = False
    def set_usage_quota():
        return True
    def get_profile_picture_html():
        return ""
    def update_user_profile():
        return True

# Set page configuration
st.set_page_config(
    page_title="Sage: Personal AI",
    page_icon="🔆",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# Define available models
MODELS = {
    # OpenAI models
    "gpt-4o": {"provider": "openai", "name": "GPT-4o"},
    "gpt-4o-mini": {"provider": "openai", "name": "GPT-4o Mini"},
    "gpt-4-turbo": {"provider": "openai", "name": "GPT-4 Turbo"},
    "gpt-3.5-turbo": {"provider": "openai", "name": "GPT-3.5 Turbo"},
    
    # Anthropic models
    "claude-3-opus": {"provider": "anthropic", "name": "Claude 3 Opus"},
    "claude-3-sonnet": {"provider": "anthropic", "name": "Claude 3 Sonnet"},
    "claude-3-haiku": {"provider": "anthropic", "name": "Claude 3 Haiku"},
}

# Function to toggle settings view
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
    # Track API usage
    if "api_calls_today" in st.session_state:
        st.session_state.api_calls_today += 1
    
    # Calculate input tokens
    input_text = " ".join([msg["content"] for msg in messages])
    input_tokens = num_tokens_from_string(input_text, model)
    
    # Check if model is one of the newer models that doesn't support temperature
    o_models = ["o1", "o1-mini", "o3-mini"]
    
    # Create parameters dictionary
    params = {
        "model": model,
        "messages": messages,
    }
    
    # Add temperature parameter only for models that support it
    if not any(o_model in model for o_model in o_models):
        params["temperature"] = 0.7
    
    response = openai_client.chat.completions.create(**params)
    response_text = response.choices[0].message.content
    
    # Calculate output tokens
    output_tokens = num_tokens_from_string(response_text, model)
    
    # Update user spending if authenticated
    if st.session_state.get("authenticated", False) and st.session_state.get("current_user"):
        username = st.session_state.get("current_user")
        update_user_spending(username, model, input_tokens, output_tokens)
    
    return response_text

# Function to get chat response from Anthropic
@api_error_handler("anthropic")
def get_anthropic_response(messages, model):
    # Track API usage
    if "api_calls_today" in st.session_state:
        st.session_state.api_calls_today += 1
    
    # Calculate input tokens
    input_text = " ".join([msg["content"] for msg in messages])
    input_tokens = num_tokens_from_string(input_text, model)
    
    # Convert messages to Anthropic format
    anthropic_messages = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        anthropic_messages.append({"role": role, "content": msg["content"]})
    
    # All current Claude models support these parameters
    response = anthropic_client.messages.create(
        model=model,
        messages=anthropic_messages,
        temperature=0.7,
        max_tokens=1000
    )
    response_text = response.content[0].text
    
    # Calculate output tokens
    output_tokens = num_tokens_from_string(response_text, model)
    
    # Update user spending if authenticated
    if st.session_state.get("authenticated", False) and st.session_state.get("current_user"):
        username = st.session_state.get("current_user")
        update_user_spending(username, model, input_tokens, output_tokens)
    
    return response_text

# Function to get chat response
@handle_error
def get_chat_response(messages, model_info):
    provider = model_info["provider"]
    model = st.session_state.model
    
    if provider == "openai":
        return get_openai_response(messages, model)
    elif provider == "anthropic":
        return get_anthropic_response(messages, model)
    else:
        raise ModelNotAvailableError(f"Provider {provider} not supported")

# Authentication check
if auth_enabled and not check_password():
    st.stop()

# Load user-specific chats after authentication
if "chats" not in st.session_state and st.session_state.get("current_user"):
    username = st.session_state.get("current_user")
    st.session_state.chats = load_user_chats(username)

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Settings page
if st.session_state.show_settings:
    st.title("Settings")
    
    with st.container():
        st.markdown('<div class="settings-container">', unsafe_allow_html=True)
        
        st.subheader("User Profile Settings")
        
        # Display current username (not editable)
        username = st.session_state.get("current_user", "")
        display_name = st.session_state.get("user_profile", {}).get("display_name", username)
        st.info(f"Logged in as: {display_name}")
        
        # Password change section
        st.markdown("### Set a new password for your account")
        
        # Password fields
        st.markdown('<div class="settings-field">', unsafe_allow_html=True)
        st.text_input("New Password", type="password", key="new_password", 
                      help="Enter your new password")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="settings-field">', unsafe_allow_html=True)
        st.text_input("Confirm New Password", type="password", key="confirm_password",
                     help="Confirm your new password")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Save button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Save Changes", on_click=update_settings, use_container_width=True):
                pass
        with col2:
            if st.button("Back to Chat", on_click=toggle_settings, use_container_width=True):
                pass
        
        # Show error/success messages
        if "settings_error" in st.session_state and st.session_state["settings_error"]:
            st.error(st.session_state["settings_error"])
            st.session_state["settings_error"] = ""
        
        if "settings_success" in st.session_state and st.session_state["settings_success"]:
            st.success("Password updated successfully!")
            st.session_state["settings_success"] = False
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Stop rendering the rest of the app
    st.stop()

# Sidebar
with st.sidebar:
    # User profile information
    if st.session_state.get("authenticated", False) and st.session_state.get("user_profile"):
        user_profile = st.session_state["user_profile"]
        username = st.session_state.get("current_user", "User")
        display_name = user_profile.get("display_name", username)
        total_spending = user_profile.get("total_spending", 0.0)
        
        # Display user info
        st.markdown(
            f"""
            <div class="user-info">
                <div class="user-avatar">
                    {get_profile_picture_html()}
                </div>
                <div class="user-details">
                    <div class="user-name">{display_name}</div>
                    <div class="user-spending">Total Spent: {format_currency(total_spending)}</div>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Model selection
    st.markdown("### Model")
    model_options = list(MODELS.keys())
    selected_model = st.selectbox(
        "Select a model",
        options=model_options,
        index=model_options.index(st.session_state.model) if st.session_state.model in model_options else 0,
        format_func=lambda x: MODELS[x]["name"]
    )
    
    if selected_model != st.session_state.model:
        st.session_state.model = selected_model
    
    # Display provider info
    selected_model_info = MODELS[st.session_state.model]
    st.caption(f"Provider: {selected_model_info['provider'].upper()}")
    
    # New chat button - moved above history
    st.markdown('<div class="new-chat-button">', unsafe_allow_html=True)
    if st.button("💬 New Chat", key="new_chat", use_container_width=True):
        create_new_chat()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat history - only show current user's chats
    if st.session_state.chats:
        st.markdown("### History")
        
        # Get current username
        current_user = st.session_state.get("current_user")
        
        # Filter chats to only show those belonging to the current user
        user_chats = {
            chat_id: chat for chat_id, chat in st.session_state.chats.items()
            if chat.get("user") == current_user or "user" not in chat  # Include chats without user field for backward compatibility
        }
        
        # Sort chats by creation time (newest first)
        sorted_chats = sorted(
            user_chats.items(),
            key=lambda x: x[1].get("created_at", ""),
            reverse=True
        )
        
        # Create a container for history buttons to apply consistent styling
        history_container = st.container()
        with history_container:
            for chat_id, chat in sorted_chats:
                # Create a fixed-width container for each button
                col1, col2 = st.columns([1, 0.001])  # The second column is just a spacer
                with col1:
                    if st.button(chat["title"], key=f"chat_{chat_id}", use_container_width=True, help="Click to open this chat"):
                        st.session_state.current_chat_id = chat_id
                        st.rerun()
    
    # Add spending details at the bottom of the sidebar
    if st.session_state.get("authenticated", False) and st.session_state.get("user_profile"):
        st.markdown('<div class="sidebar-footer">', unsafe_allow_html=True)
        user_profile = st.session_state["user_profile"]
        model_usage = user_profile.get("model_usage", {})
        
        with st.expander("View Spending Details"):
            # Add refresh button at the top of the spending details - centered
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="refresh-button">', unsafe_allow_html=True)
                if st.button("🔄 Refresh", key="refresh_spending", help="Refresh spending data", on_click=refresh_spending_data):
                    pass
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Show success message if refresh was successful
            if st.session_state.get("refresh_success"):
                st.success("Spending data refreshed!")
                st.session_state["refresh_success"] = False
                # Get updated data
                user_profile = st.session_state["user_profile"]
                model_usage = user_profile.get("model_usage", {})
            
            st.markdown("<div class='spending-details'>", unsafe_allow_html=True)
            st.markdown(f"**Total Spending**: {format_currency(user_profile.get('total_spending', 0.0))}")
            
            if model_usage:
                st.markdown("**Model Usage**:")
                for model, usage in model_usage.items():
                    st.markdown(f"- **{model}**: {format_currency(usage.get('total_cost', 0.0))}")
                    st.markdown(f"  - Input tokens: {usage.get('input_tokens', 0):,}")
                    st.markdown(f"  - Output tokens: {usage.get('output_tokens', 0):,}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Settings button at the bottom of the sidebar
    st.markdown('<div class="settings-button">', unsafe_allow_html=True)
    if st.button("⚙️ Settings", on_click=toggle_settings, use_container_width=True):
        pass
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface
if st.session_state.current_chat_id is None or st.session_state.current_chat_id not in st.session_state.chats:
    # Create a new chat if none exists
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


