# Global pytest configuration and fixtures for skidl_generator tests
import sys
import os

# Add project root to Python path to enable imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
