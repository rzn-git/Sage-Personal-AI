"""
Logging configuration for Sage AI
"""
import logging
import logging.handlers
import os
import sys
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
def setup_logging(app_name="sage_ai"):
    """Set up logging configuration"""
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # File handler - daily rotating log file
    log_file = os.path.join("logs", f"{app_name}.log")
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep logs for 30 days
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Security event logging
def log_security_event(logger, event_type, username=None, ip_address=None, details=None):
    """Log security-related events"""
    message = f"SECURITY EVENT: {event_type}"
    if username:
        message += f" | User: {username}"
    if ip_address:
        message += f" | IP: {ip_address}"
    if details:
        message += f" | Details: {details}"
    
    logger.warning(message)

# API usage logging
def log_api_call(logger, provider, model, tokens_used, user=None):
    """Log API usage"""
    message = f"API CALL: {provider} | Model: {model} | Tokens: {tokens_used}"
    if user:
        message += f" | User: {user}"
    
    logger.info(message)

# Performance monitoring
def log_performance(logger, operation, duration_ms):
    """Log performance metrics"""
    logger.info(f"PERFORMANCE: {operation} | Duration: {duration_ms}ms") 