"""
Pytest configuration for all tests.

This file configures the Python path to allow importing from the 'app' module.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent.parent / "app"
sys.path.insert(0, str(app_dir))
