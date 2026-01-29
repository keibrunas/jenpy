"""
Global configuration for Pytest.
Sets up the python path and provides common fixtures.
"""

import os
import sys
from typing import Generator
from unittest.mock import patch

import pytest

# Add the project root to the python path so imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def clean_env() -> Generator[None, None, None]:
    """
    Fixture that automatically clears environment variables
    relevant to the application before each test.
    Ensures test isolation.
    """
    with patch.dict(os.environ, {}, clear=True):
        yield
