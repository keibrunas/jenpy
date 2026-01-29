"""
Unit tests for app.utils module.
Ensures 100% coverage for shared utilities.
"""

import logging
from unittest.mock import patch
import pytest
from google.auth.exceptions import DefaultCredentialsError

from app import utils


# --- Tests for setup_logging ---
def test_setup_logging() -> None:
    """Verify logger configuration."""
    logger = utils.setup_logging("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_setup_logging_idempotency() -> None:
    """Verify calling setup_logging twice doesn't duplicate handlers."""
    logger = utils.setup_logging("test_logger_idem")
    # Reset handlers for clean state test
    logger.handlers = []

    utils.setup_logging("test_logger_idem")
    num_handlers_initial = len(logger.handlers)

    utils.setup_logging("test_logger_idem")
    assert len(logger.handlers) == num_handlers_initial


# --- Tests for get_project_id ---
def test_get_project_id_from_env() -> None:
    """Test retrieving PROJECT_ID from environment variable."""
    with patch.dict("os.environ", {"PROJECT_ID": "env-project"}):
        assert utils.get_project_id() == "env-project"


def test_get_project_id_from_auth() -> None:
    """Test retrieving PROJECT_ID from google.auth.default."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("app.utils.google.auth.default") as mock_auth:
            # Caso Felice: Google Auth restituisce un ID valido
            mock_auth.return_value = (None, "auth-project")
            assert utils.get_project_id() == "auth-project"


def test_get_project_id_auth_returns_none() -> None:
    """
    Test the case where auth succeeds but returns None for project_id.
    This covers the Pylance fix logic.
    """
    with patch.dict("os.environ", {}, clear=True):
        with patch("app.utils.google.auth.default") as mock_auth:
            # Caso Limite: Google Auth restituisce None al posto dell'ID
            mock_auth.return_value = (None, None)

            with pytest.raises(
                ValueError, match="GCP Credentials found, but no Project ID associated"
            ):
                utils.get_project_id()


def test_get_project_id_failure() -> None:
    """Test failure when PROJECT_ID is missing and auth fails completely."""
    with patch.dict("os.environ", {}, clear=True):
        with patch("app.utils.google.auth.default") as mock_auth:
            mock_auth.side_effect = DefaultCredentialsError("Auth failed")

            with pytest.raises(ValueError, match="Missing Project ID"):
                utils.get_project_id()
