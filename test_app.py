import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import get_chat_title_from_content, format_timestamp, ensure_data_dir
from error_handler import APIError, ModelNotAvailableError

class TestChatBot(unittest.TestCase):
    """Test cases for the Personal AI Chat Bot"""
    
    def test_get_chat_title_from_content(self):
        """Test the get_chat_title_from_content function"""
        content = "This is a test message"
        title = get_chat_title_from_content(content)
        self.assertEqual(title, "This is a test...")
        
        # Test with longer content
        content = "This is a longer test message with more than four words"
        title = get_chat_title_from_content(content)
        self.assertEqual(title, "This is a longer...")
        
        # Test with custom max_words
        content = "This is a test message"
        title = get_chat_title_from_content(content, max_words=2)
        self.assertEqual(title, "This is...")
    
    def test_format_timestamp(self):
        """Test the format_timestamp function"""
        # Test with no arguments
        timestamp = format_timestamp()
        self.assertIsInstance(timestamp, str)
        
        # Test with a timestamp string
        timestamp_str = "2023-01-01T12:00:00"
        formatted = format_timestamp(timestamp_str)
        self.assertEqual(formatted, "2023-01-01 12:00:00")
    
    def test_ensure_data_dir(self):
        """Test the ensure_data_dir function"""
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs:
            ensure_data_dir()
            mock_makedirs.assert_called_once()
    
    def test_api_error(self):
        """Test the APIError class"""
        error = APIError("Test error")
        self.assertEqual(str(error), "Test error")
    
    def test_model_not_available_error(self):
        """Test the ModelNotAvailableError class"""
        error = ModelNotAvailableError("Test error")
        self.assertEqual(str(error), "Test error")

if __name__ == "__main__":
    unittest.main() 