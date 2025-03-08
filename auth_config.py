"""
Authentication configuration for Sage AI
"""
import os
import streamlit as st
import hmac
import json
import datetime
import base64
from utils import load_user_data, save_user_data

def check_password():
    """Returns `True` if the user had the correct password and is an allowed user."""
    
    # Add debugging
    st.write(f"DEBUG - check_password called")
    st.write(f"DEBUG - signup_mode: {st.session_state.get('signup_mode', False)}")
    st.write(f"DEBUG - authenticated: {st.session_state.get('authenticated', False)}")
    
    # Check if we're in signup mode
    if st.session_state.get("signup_mode", False):
        return show_signup_form()
    
    # Try to get allowed users from Streamlit secrets first, then fall back to environment variables
    allowed_users_str = None
    
    # Check if we have secrets configured
    if "auth" in st.secrets and "allowed_users" in st.secrets["auth"]:
        allowed_users_str = st.secrets["auth"]["allowed_users"]
    else:
        # Fall back to environment variable
        allowed_users_str = os.environ.get("ALLOWED_USERS")
    
    # Check if ALLOWED_USERS is set
    if not allowed_users_str:
        st.error("No users configured. Please set the ALLOWED_USERS environment variable or secret.")
        st.info("For Streamlit Cloud deployment, configure this in the app settings.")
        return False
        
    try:
        allowed_users = json.loads(allowed_users_str)
    except json.JSONDecodeError:
        st.error("Error in ALLOWED_USERS configuration. Please check the JSON format.")
        return False
    
    # Check if we have allowed_users in session state (for users created during this session)
    if "allowed_users" in st.session_state:
        allowed_users.update(st.session_state["allowed_users"])
    
    # Load users from users.json as well (for users who signed up)
    user_data = load_user_data()
    for username, user_info in user_data.items():
        if "password" in user_info and username not in allowed_users:
            allowed_users[username] = user_info["password"]
    
    # Store the combined allowed_users in session state for future use
    st.session_state["allowed_users"] = allowed_users
    
    def credentials_entered():
        """Checks whether credentials entered by the user are correct."""
        # Get username and password from session state
        # Use auth_username and auth_password to avoid conflicts with app.py
        username = st.session_state["auth_username"]
        password = st.session_state["auth_password"]
        
        # Add debugging
        st.write(f"DEBUG - Login attempt for username: {username}")
        
        # Get the latest allowed_users from session state
        current_allowed_users = st.session_state.get("allowed_users", {})
        
        # Add debugging
        st.write(f"DEBUG - Current allowed_users: {current_allowed_users}")
        st.write(f"DEBUG - Username in allowed_users: {username in current_allowed_users}")
        if username in current_allowed_users:
            st.write(f"DEBUG - Password match: {password == current_allowed_users[username]}")
        
        if username in current_allowed_users and password == current_allowed_users[username]:
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = username
            
            # Load user profile data
            load_user_profile(username)
            
            # Initialize chat-related session state variables
            if "chats" not in st.session_state:
                st.session_state.chats = {}
            
            if "current_chat_id" not in st.session_state:
                st.session_state.current_chat_id = None
            
            # Don't store the password
            del st.session_state["auth_password"]
            del st.session_state["auth_username"]
            
            # Add debugging
            st.write(f"DEBUG - Authentication successful for: {username}")
            st.write(f"DEBUG - Authentication state: {st.session_state.get('authenticated', False)}")
            st.write(f"DEBUG - Current user: {st.session_state.get('current_user', 'None')}")
            
            # Force a rerun to refresh the page
            st.rerun()
        else:
            st.session_state["authenticated"] = False
            st.write(f"DEBUG - Authentication failed for: {username}")

    # Don't show the login form if already authenticated
    if st.session_state.get("authenticated", False):
        return True
        
    # Show login form
    st.title("🔆 Sage: Personal AI")
    st.write("Please enter your credentials to access this application.")
    
    # Username and password fields - use auth_username and auth_password as keys
    st.text_input("Username", key="auth_username")
    st.text_input("Password", type="password", key="auth_password")
    
    # Login button with green styling
    st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: #4CAF50;
            color: white;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #45a049;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    st.button("Login", on_click=credentials_entered, key="auth_login_button")
    
    # Sign up option
    st.write("Don't have an account? Sign Up")
    st.button("Sign Up", on_click=lambda: set_signup_mode(True), key="auth_signup_button")
    
    # Show error message if authentication failed
    if "authenticated" in st.session_state:
        if not st.session_state["authenticated"]:
            st.error("😕 Invalid username or password")
    
    return False

def set_signup_mode(enabled):
    """Set whether we're in signup mode"""
    st.session_state["signup_mode"] = enabled
    # Force a rerun to show the signup form immediately
    if enabled:
        st.rerun()

def show_signup_form():
    """Show the signup form and handle user registration"""
    
    # Show signup form with title and subtitle
    st.title("🔆 Sage: Personal AI - Sign Up")
    st.write("Create a new account to access this application.")
    
    # Initialize session state variables for the form
    if "signup_username" not in st.session_state:
        st.session_state["signup_username"] = ""
    if "signup_password" not in st.session_state:
        st.session_state["signup_password"] = ""
    if "signup_confirm_password" not in st.session_state:
        st.session_state["signup_confirm_password"] = ""
    if "signup_display_name" not in st.session_state:
        st.session_state["signup_display_name"] = ""
    
    # Function to handle signup form submission
    def handle_signup():
        """Handle signup form submission"""
        # Get values from session state
        username = st.session_state["signup_username"]
        password = st.session_state["signup_password"]
        confirm_password = st.session_state["signup_confirm_password"]
        display_name = st.session_state["signup_display_name"] or username
        
        # Add debugging
        st.write(f"DEBUG - Signup attempt for username: {username}")
        
        # Validate inputs
        if not username or not password:
            st.session_state["signup_error"] = "Username and password are required"
            return
        
        if password != confirm_password:
            st.session_state["signup_error"] = "Passwords do not match"
            return
        
        # Check if username already exists
        user_data = load_user_data()
        if username in user_data:
            st.session_state["signup_error"] = "Username already exists"
            return
        
        # Create new user
        if username not in user_data:
            user_data[username] = {
                "display_name": display_name,
                "password": password,
                "profile_picture": None,
                "total_spending": 0.0,
                "model_usage": {},
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            # Add debugging
            st.write(f"DEBUG - Creating new user: {username}")
            
            # Save user data
            save_user_data(user_data)
            
            # Create user directory for chat data
            user_dir = os.path.join("chat_data", username)
            os.makedirs(user_dir, exist_ok=True)
            
            # Also add to allowed_users for immediate login
            if "allowed_users" not in st.session_state:
                st.session_state["allowed_users"] = {}
            st.session_state["allowed_users"][username] = password
            
            # Add debugging
            st.write(f"DEBUG - Added to allowed_users: {username}")
            st.write(f"DEBUG - Current allowed_users: {st.session_state['allowed_users']}")
            
            # Set success message and reset form
            st.session_state["signup_success"] = True
            st.session_state["signup_mode"] = False
            
            # Automatically authenticate the user
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = username
            
            # Initialize chat-related session state variables
            if "chats" not in st.session_state:
                st.session_state.chats = {}
            
            if "current_chat_id" not in st.session_state:
                st.session_state.current_chat_id = None
            
            # Load user profile data
            load_user_profile(username)
            
            # Add debugging
            st.write(f"DEBUG - User authenticated after signup: {username}")
            st.write(f"DEBUG - Authentication state: {st.session_state.get('authenticated', False)}")
            st.write(f"DEBUG - Current user: {st.session_state.get('current_user', 'None')}")
            
            # Force a rerun to refresh the page
            st.rerun()

    # Don't show the signup form if already successful
    if st.session_state.get("signup_success", False):
        return True
        
    # Show signup form
    st.text_input("Username", key="signup_username", value=st.session_state.get("signup_username", ""))
    st.text_input("Password", type="password", key="signup_password", value=st.session_state.get("signup_password", ""))
    st.text_input("Confirm Password", type="password", key="signup_confirm_password", value=st.session_state.get("signup_confirm_password", ""))
    st.text_input("Display Name", key="signup_display_name", value=st.session_state.get("signup_display_name", ""))
    
    # Sign up button with green styling
    st.markdown("""
        <style>
        div[data-testid="stButton"] button {
            background-color: #4CAF50;
            color: white;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #45a049;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    st.button("Sign Up", on_click=handle_signup, key="signup_button")
    
    # Show error message if signup failed
    if "signup_error" in st.session_state:
        st.error(st.session_state["signup_error"])
    
    return False

def load_user_profile(username):
    """Load user profile data"""
    user_data = load_user_data()
    if username in user_data:
        st.session_state["user_profile"] = user_data[username]
        return True
    return False

def save_user_profile(username, profile_data):
    """Save user profile data"""
    user_data = load_user_data()
    if username in user_data:
        user_data[username].update(profile_data)
        save_user_data(user_data)
        return True
    return False

def get_profile_picture_html(username=None):
    """Get HTML for user profile picture"""
    if not username:
        username = st.session_state.get("current_user")
    
    if not username:
        return ""
    
    user_data = load_user_data()
    if username in user_data and "profile_picture" in user_data[username] and user_data[username]["profile_picture"]:
        # If user has a profile picture, use it
        profile_pic = user_data[username]["profile_picture"]
        return f'<img src="data:image/png;base64,{profile_pic}" style="width:50px;height:50px;border-radius:50%;">'
    else:
        # Default avatar with first letter of username
        first_letter = username[0].upper()
        return f'<div style="width:50px;height:50px;border-radius:50%;background-color:#4CAF50;color:white;display:flex;align-items:center;justify-content:center;font-size:24px;">{first_letter}</div>'

def set_usage_quota():
    """Check and set usage quota for the current user"""
    if not st.session_state.get("authenticated", False):
        return False
    
    username = st.session_state.get("current_user")
    if not username:
        return False
    
    # Load user data
    user_data = load_user_data()
    if username not in user_data:
        return False
    
    # Check if user has a spending limit
    if "spending_limit" in user_data[username]:
        spending_limit = user_data[username]["spending_limit"]
        current_spending = user_data[username].get("total_spending", 0.0)
        
        # If user is over their limit, show a warning
        if current_spending >= spending_limit:
            st.warning(f"You have reached your spending limit of ${spending_limit:.2f}. Please contact the administrator to increase your limit.")
            return False
    
    return True

def update_user_profile():
    """Update user profile with form data"""
    if not st.session_state.get("authenticated", False):
        return False
    
    username = st.session_state.get("current_user")
    if not username:
        return False
    
    # Get values from session state
    display_name = st.session_state.get("profile_display_name", "")
    new_password = st.session_state.get("profile_new_password", "")
    confirm_password = st.session_state.get("profile_confirm_password", "")
    
    # Validate inputs
    if new_password and new_password != confirm_password:
        st.error("Passwords do not match")
        return False
    
    # Update user data
    user_data = load_user_data()
    
    if username in user_data:
        # Update display name if provided
        if display_name:
            user_data[username]["display_name"] = display_name
        
        # Update password if provided
        if new_password:
            user_data[username]["password"] = new_password
        
        # Save updated user data
        save_user_data(user_data)
        
        # Update session state
        st.session_state["user_profile"] = user_data[username]
        
        return True
    
    return False

            #