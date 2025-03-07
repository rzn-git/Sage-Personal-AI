import streamlit as st
import uuid
import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from utils import save_chats, load_chats, get_chat_title_from_content, format_timestamp
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
    from auth_config import check_password, set_usage_quota
    auth_enabled = True
except ImportError:
    auth_enabled = False
    def set_usage_quota():
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
        background-color: #e9ebef;
        color: black;
        border-radius: 5px;
        border: none;
        padding: 10px 24px;
        font-size: 16px;
        text-align: left;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #d3d7df;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
    }
    .chat-message.user {
        background-color: #2b313e;
        margin-left: auto;
        margin-right: 0;
        text-align: right;
        max-width: 80%;
    }
    .chat-message.assistant {
        background-color: #475063;
        margin-right: auto;
        margin-left: 0;
        text-align: left;
        max-width: 80%;
    }
    .stTextInput input {
        border-radius: 5px;
        color: black;
    }
    .stSelectbox {
        border-radius: 5px;
    }
    .stSelectbox > div > div {
        background-color: #d3d7df;
        border-radius: 5px;
        color: black;
    }
    .stMarkdown h3 {
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        text-align: left;
        color: black;
    }
    .stCaption {
        font-style: italic;
        margin-bottom: 1rem;
        text-align: left;
        color: black;
    }
    .sidebar .stButton button {
        text-align: left !important;
        justify-content: flex-start !important;
        align-items: flex-start !important;
        display: flex !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Right-align user messages and avatar */
    [data-testid="stChatMessageContent"] {
        width: 100%;
    }
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        display: flex;
        flex-direction: column;
    }
    [data-testid="stChatMessage"].user [data-testid="stChatMessageContent"] {
        align-items: flex-end;
    }
    [data-testid="stChatMessage"].assistant [data-testid="stChatMessageContent"] {
        align-items: flex-start;
    }
    
    /* Flip the user avatar to the right side */
    [data-testid="stChatMessage"].user {
        flex-direction: row-reverse;
    }
    [data-testid="stChatMessage"].user > div:first-child {
        margin-right: 0;
        margin-left: 0.5rem;
    }
    
    /* Make user messages have a different color */
    [data-testid="stChatMessage"].user [data-testid="stChatMessageContent"] > div {
        background-color: #3182ce;
        color: black;
        border-radius: 1rem 0 1rem 1rem;
    }
    
    /* Style assistant messages */
    [data-testid="stChatMessage"].assistant [data-testid="stChatMessageContent"] > div {
        background-color: #4a5568;
        color: black;
        border-radius: 0 1rem 1rem 1rem;
    }
    
    /* Ensure chat history container has fixed width */
    .sidebar [data-testid="stVerticalBlock"] {
        width: 100% !important;
    }
    
    /* Ensure all buttons in the sidebar have fixed width */
    .sidebar .stButton {
        width: 100% !important;
    }
    
    /* Fix the width of the button container in the sidebar */
    .sidebar [data-testid="stHorizontalBlock"] {
        width: 100% !important;
    }
    
    /* Fix the width of columns in the sidebar */
    .sidebar [data-testid="column"] {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Ensure chat history buttons have fixed width and consistent appearance */
    .sidebar .stButton button {
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;
        overflow: hidden !important;
    }
    
    .sidebar .stButton button span {
        text-align: left !important;
        width: 100% !important;
        display: block !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
    }
    
    /* Make all text black */
    body, p, span, h1, h2, h3, h4, h5, h6, div, label, button {
        color: black !important;
    }
    
    /* Ensure chat history titles are left-aligned */
    .sidebar h3 {
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# Define available models
MODELS = {
    "OpenAI gpt-4o-mini": {"provider": "openai", "model": "gpt-4o-mini"}, 
    "Anthropic claude-3-5-haiku-20241022": {"provider": "anthropic", "model": "claude-3-5-haiku-20241022"},
    "OpenAI o3-mini": {"provider": "openai", "model": "o3-mini"},    
    "OpenAI o1-mini": {"provider": "openai", "model": "o1-mini"},           
    "OpenAI gpt-4o": {"provider": "openai", "model": "gpt-4o"}, 
    "Anthropic claude-3-7-sonnet-20250219": {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"},
    "OpenAI o1": {"provider": "openai", "model": "o1"}     
}

# Initialize session state variables
if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "model" not in st.session_state:
    st.session_state.model = list(MODELS.keys())[0]

# Check authentication if enabled
if auth_enabled and not check_password():
    st.stop()  # Stop execution if authentication fails

# Check usage quota
if not set_usage_quota():
    st.stop()  # Stop execution if quota exceeded

# Function to create a new chat
@handle_error
def create_new_chat():
    chat_id = str(uuid.uuid4())
    timestamp = format_timestamp()
    st.session_state.chats[chat_id] = {
        "id": chat_id,
        "title": f"New Chat ({timestamp})",
        "messages": [],
        "created_at": timestamp
    }
    st.session_state.current_chat_id = chat_id
    save_chats(st.session_state.chats)
    return chat_id

# Function to get chat response from OpenAI
@api_error_handler("openai")
def get_openai_response(messages, model):
    # Track API usage
    if "api_calls_today" in st.session_state:
        st.session_state.api_calls_today += 1
        
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
    return response.choices[0].message.content

# Function to get chat response from Anthropic
@api_error_handler("anthropic")
def get_anthropic_response(messages, model):
    # Track API usage
    if "api_calls_today" in st.session_state:
        st.session_state.api_calls_today += 1
        
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
    return response.content[0].text

# Function to get chat response
@handle_error
def get_chat_response(messages, model_info):
    provider = model_info["provider"]
    model = model_info["model"]
    
    # Check if API keys are available
    if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
        raise ModelNotAvailableError("OpenAI API key not found. Please add it to your .env file.")
    
    if provider == "anthropic" and not os.getenv("ANTHROPIC_API_KEY"):
        raise ModelNotAvailableError("Anthropic API key not found. Please add it to your .env file.")
    
    try:
        if provider == "openai":
            try:
                return get_openai_response(messages, model)
            except Exception as e:
                error_msg = str(e)
                if "model_not_found" in error_msg or "does not exist" in error_msg:
                    return f"Error: The model '{model}' is not available or you don't have access to it. Please select a different model."
                raise
        elif provider == "anthropic":
            try:
                return get_anthropic_response(messages, model)
            except Exception as e:
                error_msg = str(e)
                if "model not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                    return f"Error: The model '{model}' is not available or you don't have access to it. Please select a different model."
                raise
        else:
            raise ModelNotAvailableError(f"Provider {provider} not supported")
    except Exception as e:
        return f"Error: {str(e)}"

# Sidebar
with st.sidebar:
    st.title("🔆Sage: Personal AI")
    
    # New chat button
    if st.button("New Chat", use_container_width=True):
        create_new_chat()
    
    # Model selection
    st.markdown("### Select Model")
    st.session_state.model = st.selectbox(
        "Choose an AI model",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index(st.session_state.model),
        format_func=lambda x: x.replace("OpenAI ", "").replace("Anthropic ", ""),
        help="Select the AI model to use for generating responses"
    )
    
    # Display provider info
    selected_model_info = MODELS[st.session_state.model]
    st.caption(f"Provider: {selected_model_info['provider'].upper()}")
    
    # Chat history
    if st.session_state.chats:
        st.markdown("### History")
        # Sort chats by creation time (newest first)
        sorted_chats = sorted(
            st.session_state.chats.items(),
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
    
    # Save chats to disk
    save_chats(st.session_state.chats)


