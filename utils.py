import json
import os
import datetime
import tiktoken

# Define the path for storing chat data
CHAT_DATA_DIR = "chat_data"
CHAT_DATA_FILE = os.path.join(CHAT_DATA_DIR, "chats.json")
USER_DATA_FILE = os.path.join(CHAT_DATA_DIR, "users.json")

# Model pricing per million tokens (based on the provided price chart)
MODEL_PRICING = {
    # OpenAI models
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 0.50, "output": 1.50},
    "gpt-4o-2024": {"input": 2.50, "output": 10.00},
    "gpt-4-preview": {"input": 10.00, "output": 30.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4-1106-preview": {"input": 10.00, "output": 30.00},
    "gpt-4-0125-preview": {"input": 10.00, "output": 30.00},
    "gpt-4-32k": {"input": 60.00, "output": 120.00},
    "gpt-4-32k-0613": {"input": 60.00, "output": 120.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-4-0613": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-1106": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-0125": {"input": 0.50, "output": 1.50},
    
    # Anthropic models
    "claude-3-opus": {"input": 15.00, "output": 60.00},
    "claude-3-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.80, "output": 4.00},
    "claude-2.1": {"input": 8.00, "output": 24.00},
    "claude-2.0": {"input": 8.00, "output": 24.00},
    "claude-instant-1.2": {"input": 1.60, "output": 5.50},
    "o1-mini-2": {"input": 1.10, "output": 4.40},
    "o1-mini": {"input": 1.10, "output": 4.40},
    "o3-mini-2": {"input": 1.10, "output": 4.40},
    "o3-mini": {"input": 1.10, "output": 4.40},
}

# Token counters for different models
def num_tokens_from_string(string, model):
    """Returns the number of tokens in a text string for a specific model"""
    # For OpenAI models
    if "gpt" in model.lower():
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(string))
        except:
            # Fallback to cl100k_base encoding for newer models
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(string))
    
    # For Anthropic models (Claude)
    # Using a simple approximation: ~4 characters per token
    return len(string) // 4

def calculate_cost(tokens, model, is_input=True):
    """Calculate cost based on token count and model"""
    if model not in MODEL_PRICING:
        # Default to a reasonable price if model not found
        return 0.0
    
    price_category = "input" if is_input else "output"
    # Convert price from per million tokens to per token
    price_per_token = MODEL_PRICING[model][price_category] / 1_000_000
    return tokens * price_per_token

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

def save_user_data(user_data):
    """Save user data to disk"""
    ensure_data_dir()
    
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f, indent=2)

def load_user_data():
    """Load user data from disk"""
    ensure_data_dir()
    
    if not os.path.exists(USER_DATA_FILE):
        return {}
    
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Return empty dict if file is corrupted or doesn't exist
        return {}

def update_user_spending(username, model, input_tokens, output_tokens):
    """Update user spending based on token usage"""
    user_data = load_user_data()
    
    # Initialize user data if not exists
    if username not in user_data:
        user_data[username] = {
            "total_spending": 0.0,
            "model_usage": {},
            "last_updated": datetime.datetime.now().isoformat()
        }
    
    # Calculate costs
    input_cost = calculate_cost(input_tokens, model, is_input=True)
    output_cost = calculate_cost(output_tokens, model, is_input=False)
    total_cost = input_cost + output_cost
    
    # Update user data
    user_data[username]["total_spending"] += total_cost
    
    # Update model-specific usage
    if model not in user_data[username]["model_usage"]:
        user_data[username]["model_usage"][model] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_cost": 0.0
        }
    
    user_data[username]["model_usage"][model]["input_tokens"] += input_tokens
    user_data[username]["model_usage"][model]["output_tokens"] += output_tokens
    user_data[username]["model_usage"][model]["total_cost"] += total_cost
    user_data[username]["last_updated"] = datetime.datetime.now().isoformat()
    
    # Save updated user data
    save_user_data(user_data)
    
    return total_cost

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

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.6f}" 