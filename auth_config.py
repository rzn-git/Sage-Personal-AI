"""
Authentication configuration for Sage AI
"""
import os
import streamlit as st
import hmac
import json
import datetime

def check_password():
    """Returns `True` if the user had the correct password and is an allowed user."""
    
    # Get allowed users from environment variable (JSON string)
    allowed_users_str = os.environ.get("ALLOWED_USERS", '{"admin": "admin"}')
    try:
        allowed_users = json.loads(allowed_users_str)
    except json.JSONDecodeError:
        st.error("Error in ALLOWED_USERS configuration")
        allowed_users = {"admin": "admin"}
    
    def credentials_entered():
        """Checks whether credentials entered by the user are correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]
        
        if username in allowed_users and hmac.compare_digest(password, allowed_users[username]):
            st.session_state["authenticated"] = True
            # Don't store the password
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["authenticated"] = False

    # Return True if the user is authenticated
    if st.session_state.get("authenticated", False):
        return True

    # Show login form
    st.title("🔆 Sage: Personal AI")
    st.write("Please enter your credentials to access this application.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Username", key="username")
    with col2:
        st.text_input("Password", type="password", key="password")
    
    st.button("Login", on_click=credentials_entered)
    
    if "authenticated" in st.session_state:
        if not st.session_state["authenticated"]:
            st.error("😕 Invalid username or password")
    
    return False

def set_usage_quota():
    """Sets and tracks usage quota for the current user."""
    # Initialize usage tracking
    if "api_calls_today" not in st.session_state:
        st.session_state.api_calls_today = 0
        st.session_state.last_usage_date = None
    
    # Reset counter if it's a new day
    today = str(datetime.date.today())
    if st.session_state.last_usage_date != today:
        st.session_state.api_calls_today = 0
        st.session_state.last_usage_date = today
    
    # Get max daily calls from environment variable
    max_daily_calls = int(os.environ.get("MAX_DAILY_CALLS", "50"))
    
    # Check if user has exceeded quota
    if st.session_state.api_calls_today >= max_daily_calls:
        st.error(f"You've reached your daily limit of {max_daily_calls} API calls. Please try again tomorrow.")
        return False
    
    return True 