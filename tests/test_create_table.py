"""
Unit tests for the app.create_table module.
Designed to achieve 100% code coverage.
"""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from google.api_core.exceptions import NotFound

from app import create_table

# NOTA: I test specifici su "get_project_id" (env vs auth) sono stati spostati
# in test_utils.py. Qui testiamo solo che create_table USI la funzione.


# --- Tests for load_schema ---
def test_load_schema_success() -> None:
    """Test loading a valid JSON schema."""
    mock_json = '[{"name": "col1", "type": "STRING"}]'
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.open", mock_open(read_data=mock_json)):
            with patch("google.cloud.bigquery.SchemaField.from_api_repr") as mock_from:
                mock_from.side_effect = lambda x: x
                result = create_table.load_schema(Path("dummy.json"))
                assert len(result) == 1


def test_load_schema_file_not_found() -> None:
    """Test error when schema file is missing."""
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError):
            create_table.load_schema(Path("missing.json"))


# --- Tests for create_table_logic ---
def test_create_table_logic_exists() -> None:
    """Test logic when table already exists (should not create)."""
    mock_client = MagicMock()
    mock_client.project = "test-project"  # Fix for BigQuery lib validation
    mock_client.get_table.return_value = MagicMock()

    create_table.create_table_logic(mock_client, "ds", "tbl")
    mock_client.create_table.assert_not_called()


def test_create_table_logic_creates_new() -> None:
    """Test logic when table does not exist (should create)."""
    mock_client = MagicMock()
    mock_client.project = "test-project"  # Fix for BigQuery lib validation
    mock_client.get_table.side_effect = NotFound("Table not found")

    with patch("app.create_table.load_schema", return_value=[]):
        create_table.create_table_logic(mock_client, "ds", "tbl")

    mock_client.create_table.assert_called_once()


# --- Tests for main ---
@patch("app.create_table.sys.exit")
def test_main_missing_env_vars(mock_exit: MagicMock) -> None:
    """Test main exits if required env vars are missing."""
    with patch.dict("os.environ", {"TABLE_ID": "tbl"}, clear=True):
        create_table.main()
        mock_exit.assert_called_with(1)


@patch("app.create_table.sys.exit")
@patch("app.create_table.bigquery.Client")
# Qui mockiamo solo il RITORNO della funzione, non la logica interna
@patch("app.create_table.get_project_id", return_value="proj")
@patch("app.create_table.create_table_logic")
def test_main_success(
    mock_logic: MagicMock,
    _mock_get_pid: MagicMock,  # Underscore per Pylint
    mock_client_cls: MagicMock,
    mock_exit: MagicMock,
) -> None:
    """Test main happy path."""
    with patch.dict("os.environ", {"DATASET_ID": "ds", "TABLE_ID": "tbl"}):
        create_table.main()
        mock_client_cls.assert_called_with(project="proj")
        mock_logic.assert_called_once()
        mock_exit.assert_not_called()


@patch("app.create_table.sys.exit")
@patch("app.create_table.get_project_id", return_value="proj")
@patch("app.create_table.bigquery.Client")
def test_main_exception(
    _mock_client: MagicMock, _mock_pid: MagicMock, mock_exit: MagicMock
) -> None:
    """Test main handles unexpected exceptions globally."""
    with patch.dict("os.environ", {"DATASET_ID": "ds", "TABLE_ID": "tbl"}):
        with patch("app.create_table.create_table_logic") as mock_logic:
            mock_logic.side_effect = Exception("Boom")
            create_table.main()
            mock_exit.assert_called_with(1)
