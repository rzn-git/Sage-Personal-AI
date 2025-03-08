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
    
    # Load users from users.json as well (for users who signed up)
    user_data = load_user_data()
    for username, user_info in user_data.items():
        if "password" in user_info and username not in allowed_users:
            allowed_users[username] = user_info["password"]
    
    def credentials_entered():
        """Checks whether credentials entered by the user are correct."""
        # Get username and password from session state
        # Use auth_username and auth_password to avoid conflicts with app.py
        username = st.session_state["auth_username"]
        password = st.session_state["auth_password"]
        
        if username in allowed_users and hmac.compare_digest(password, allowed_users[username]):
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = username
            
            # Load user profile data
            load_user_profile(username)
            
            # Don't store the password
            del st.session_state["auth_password"]
            del st.session_state["auth_username"]
        else:
            st.session_state["authenticated"] = False

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
            
            # Save user data
            save_user_data(user_data)
            
            # Create user directory for chat data
            user_dir = os.path.join("chat_data", username)
            os.makedirs(user_dir, exist_ok=True)
            
            # Set success message and reset form
            st.session_state["signup_success"] = True
            st.session_state["signup_mode"] = False
            
            # Clear form fields
            st.session_state["signup_username"] = ""
            st.session_state["signup_password"] = ""
            st.session_state["signup_confirm_password"] = ""
            st.session_state["signup_display_name"] = ""
    
    # Custom CSS for better UI
    st.markdown("""
        <style>
        .signup-container {
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .signup-field {
            margin-bottom: 15px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #45a049;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create signup form
    st.text_input("Username", key="signup_username")
    st.text_input("Display Name", key="signup_display_name")
    st.text_input("Password", type="password", key="signup_password")
    st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    
    # Create account button
    st.button("Create Account", on_click=handle_signup, key="signup_create_account_button")
    
    # Back to login button
    st.write("Already have an account?")
    
    def back_to_login():
        st.session_state["signup_mode"] = False
        st.rerun()
        
    st.button("Back to Login", on_click=back_to_login, key="signup_back_to_login_button")
    
    # Show error message if any
    if "signup_error" in st.session_state and st.session_state["signup_error"]:
        st.error(st.session_state["signup_error"])
        st.session_state["signup_error"] = ""
    
    # Show success message if signup was successful
    if "signup_success" in st.session_state and st.session_state["signup_success"]:
        st.success("Account created successfully! You can now log in.")
        st.session_state["signup_success"] = False
        
    return False

def load_user_profile(username):
    """Load user profile data into session state"""
    user_data = load_user_data()
    
    # Initialize user data if not exists
    if username not in user_data:
        user_data[username] = {
            "display_name": username,
            "profile_picture": None,  # Default to None
            "total_spending": 0.0,
            "model_usage": {},
            "last_updated": datetime.datetime.now().isoformat()
        }
        save_user_data(user_data)
    
    # Store user data in session state
    st.session_state["user_profile"] = user_data[username]

def update_user_profile(display_name=None, profile_picture=None):
    """Update user profile information"""
    if not st.session_state.get("authenticated", False):
        return False
    
    username = st.session_state.get("current_user")
    if not username:
        return False
    
    user_data = load_user_data()
    
    # Update display name if provided
    if display_name:
        user_data[username]["display_name"] = display_name
        st.session_state["user_profile"]["display_name"] = display_name
    
    # Update profile picture if provided
    if profile_picture is not None:
        user_data[username]["profile_picture"] = profile_picture
        st.session_state["user_profile"]["profile_picture"] = profile_picture
    
    # Save updated user data
    save_user_data(user_data)
    return True

def get_profile_picture_html():
    """Get HTML for displaying the user's profile picture"""
    if not st.session_state.get("authenticated", False):
        return ""
    
    profile = st.session_state.get("user_profile", {})
    profile_picture = profile.get("profile_picture")
    
    if profile_picture:
        # If we have a base64 encoded image
        return f'<img src="data:image/png;base64,{profile_picture}" style="width:40px;height:40px;border-radius:50%;object-fit:cover;">'
    else:
        # Default avatar with first letter of username
        display_name = profile.get("display_name", st.session_state.get("current_user", "U"))
        first_letter = display_name[0].upper()
        return f'<div style="width:40px;height:40px;border-radius:50%;background-color:#4CAF50;color:white;display:flex;align-items:center;justify-content:center;font-weight:bold;">{first_letter}</div>'

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