import json
import os
import datetime

# Define the path for storing chat data
CHAT_DATA_DIR = "chat_data"
CHAT_DATA_FILE = os.path.join(CHAT_DATA_DIR, "chats.json")

def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(CHAT_DATA_DIR):
        os.makedirs(CHAT_DATA_DIR)

def save_chats(chats):
    """Save chats to disk"""
    ensure_data_dir()
    
    # Convert datetime objects to strings if needed
    serializable_chats = {}
    for chat_id, chat in chats.items():
        serializable_chats[chat_id] = chat
    
    with open(CHAT_DATA_FILE, 'w') as f:
        json.dump(serializable_chats, f, indent=2)

def load_chats():
    """Load chats from disk"""
    ensure_data_dir()
    
    if not os.path.exists(CHAT_DATA_FILE):
        return {}
    
    try:
        with open(CHAT_DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty dict if file is corrupted or doesn't exist
        return {}

def get_chat_title_from_content(content, max_words=4):
    """Generate a chat title from the first user message"""
    words = content.split()
    title_words = words[:max_words] if len(words) > max_words else words
    return " ".join(title_words) + "..."

def format_timestamp(timestamp_str=None):
    """Format timestamp for display"""
    if timestamp_str is None:
        timestamp = datetime.datetime.now()
    else:
        try:
            timestamp = datetime.datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            timestamp = datetime.datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S") 