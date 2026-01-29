"""
Global configuration for Pytest.
Adds the project root to PYTHONPATH to allow imports of app modules.
"""

import sys
import os

# Add the project root to the python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
