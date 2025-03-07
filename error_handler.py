import streamlit as st
import logging
import traceback
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("personal_chatbot")

class ChatBotError(Exception):
    """Base exception class for chatbot errors"""
    pass

class APIError(ChatBotError):
    """Exception raised for API-related errors"""
    pass

class ModelNotAvailableError(ChatBotError):
    """Exception raised when a model is not available"""
    pass

def handle_error(func):
    """Decorator to handle errors in functions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            logger.error(f"Error in {func.__name__}: {error_msg}\n{stack_trace}")
            
            if isinstance(e, APIError):
                st.error(f"API Error: {error_msg}")
            elif isinstance(e, ModelNotAvailableError):
                st.error(f"Model Error: {error_msg}")
            else:
                st.error(f"An error occurred: {error_msg}")
            
            return None
    return wrapper

def api_error_handler(provider):
    """Handle API-specific errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_msg = str(e)
                if provider == "openai":
                    raise APIError(f"OpenAI API error: {error_msg}")
                elif provider == "anthropic":
                    raise APIError(f"Anthropic API error: {error_msg}")
                else:
                    raise APIError(f"API error: {error_msg}")
        return wrapper
    return decorator 