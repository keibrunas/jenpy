"""
Unit tests for the app.demo_pipeline module.
Achieves 100% code coverage including the main entry point.
"""

from unittest.mock import MagicMock, patch
import pytest
from google.api_core.exceptions import NotFound

from app import demo_pipeline


# --- Helper Tests (Dataset/Table checks) ---
def test_ensure_dataset_creates_if_missing() -> None:
    """Test dataset creation when NotFound."""
    mock_client = MagicMock()
    # FIX: Dobbiamo definire project come stringa, altrimenti DatasetReference fallisce
    mock_client.project = "test-project"

    mock_client.get_dataset.side_effect = NotFound("Missing")

    demo_pipeline.ensure_dataset(mock_client, "ds_id")

    mock_client.create_dataset.assert_called_once()


def test_ensure_dataset_exists() -> None:
    """Test dataset creation skipped if exists."""
    mock_client = MagicMock()
    # FIX: Project ID stringa obbligatorio per DatasetReference
    mock_client.project = "test-project"

    demo_pipeline.ensure_dataset(mock_client, "ds_id")
    mock_client.create_dataset.assert_not_called()


def test_ensure_table_creates_if_missing() -> None:
    """Test table creation when NotFound."""
    mock_client = MagicMock()
    mock_client.get_table.side_effect = NotFound("Missing")
    demo_pipeline.ensure_table(mock_client, MagicMock())
    mock_client.create_table.assert_called_once()


def test_ensure_table_exists() -> None:
    """Test table creation skipped if exists."""
    mock_client = MagicMock()
    demo_pipeline.ensure_table(mock_client, MagicMock())
    mock_client.create_table.assert_not_called()


# --- Insert & Run Logic Tests ---
def test_insert_build_log_success() -> None:
    """Test successful row insertion."""
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = []
    demo_pipeline.insert_build_log(mock_client, MagicMock(), "build-1")
    mock_client.insert_rows_json.assert_called_once()


def test_insert_build_log_failure() -> None:
    """Test exception raised on insertion errors."""
    mock_client = MagicMock()
    mock_client.insert_rows_json.return_value = [{"error": "bad data"}]
    with pytest.raises(RuntimeError, match="BigQuery Insert Errors"):
        demo_pipeline.insert_build_log(mock_client, MagicMock(), "build-1")


@patch("app.demo_pipeline.bigquery.Client")
@patch("app.demo_pipeline.ensure_dataset")
@patch("app.demo_pipeline.ensure_table")
@patch("app.demo_pipeline.insert_build_log")
def test_run_pipeline_flow(
    mock_insert: MagicMock,
    mock_ensure_tbl: MagicMock,
    mock_ensure_ds: MagicMock,
    mock_client_cls: MagicMock,
) -> None:
    """Test the orchestration logic."""
    mock_ensure_ds.return_value = MagicMock()
    demo_pipeline.run_pipeline("proj", "ds", "tbl", "1")

    mock_client_cls.assert_called_with(project="proj")
    mock_ensure_ds.assert_called()
    mock_ensure_tbl.assert_called()
    mock_insert.assert_called()


# --- MAIN ENTRY POINT TESTS ---


@patch("app.demo_pipeline.run_pipeline")
@patch("app.demo_pipeline.get_project_id", return_value="test-proj")
def test_main_success(_mock_get_pid: MagicMock, mock_run: MagicMock) -> None:
    """Test main function success path."""
    with patch.dict(
        "os.environ", {"DATASET_ID": "ds", "TABLE_ID": "tb", "BUILD_NUMBER": "1"}
    ):
        demo_pipeline.main()
        mock_run.assert_called_with("test-proj", "ds", "tb", "1")


@patch("app.demo_pipeline.sys.exit")
@patch("app.demo_pipeline.get_project_id", return_value="")
def test_main_missing_project_id(
    _mock_get_pid: MagicMock, mock_exit: MagicMock
) -> None:
    """Test main exits if project ID is missing."""
    demo_pipeline.main()
    mock_exit.assert_called_with(1)


@patch("app.demo_pipeline.sys.exit")
@patch("app.demo_pipeline.run_pipeline")
@patch("app.demo_pipeline.get_project_id", return_value="test-proj")
def test_main_exception(
    _mock_get_pid: MagicMock, mock_run: MagicMock, mock_exit: MagicMock
) -> None:
    """Test main handles exceptions from run_pipeline."""
    mock_run.side_effect = Exception("Boom")
    demo_pipeline.main()
    mock_exit.assert_called_with(1)
