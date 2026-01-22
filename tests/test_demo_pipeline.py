import pytest
from unittest.mock import MagicMock, patch
from app.demo_pipeline import run_demo 

# ✅ FIX: Patch the actual library class, not the reference in app
@patch('google.cloud.bigquery.Client')
def test_run_demo_success(mock_client_cls):
    # 1. Setup the Mock
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    # Simulate that the dataset does NOT exist
    from google.api_core.exceptions import NotFound
    mock_client.get_dataset.side_effect = NotFound("Dataset not found")
    
    # 2. Run the actual script function
    run_demo()

    # 3. Assertions
    # Verify it tried to create the missing dataset
    mock_client.create_dataset.assert_called()
    # Verify it tried to insert rows
    mock_client.insert_rows_json.assert_called()