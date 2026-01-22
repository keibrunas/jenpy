import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys

# ✅ FIX 1: Import from the correct file 'app/create_table.py'
from app.create_table import create_table_managed

# ✅ FIX 2: Patch the entire 'bigquery' module
# This ensures bigquery.Client AND bigquery.SchemaField are both mocks
@patch('app.create_table.bigquery')
# ✅ FIX 3: Patch 'sys.exit' to prevent the test from crashing
@patch('app.create_table.sys.exit')
@patch.dict('os.environ', {
    'PROJECT_ID': 'test-project', 
    'DATASET_ID': 'test_db', 
    'TABLE_ID': 'test_table'
})
def test_create_table_success(mock_sys_exit, mock_bigquery):
    # --- 1. Setup Mocks ---
    mock_client = MagicMock()
    mock_bigquery.Client.return_value = mock_client
    
    # Handle the 'SchemaField.from_api_repr' call
    # We just make it return the input dictionary itself to keep it simple
    mock_bigquery.SchemaField.from_api_repr.side_effect = lambda x: x

    # Simulate that table does NOT exist (raises NotFound) so the script tries to create it
    from google.api_core.exceptions import NotFound
    mock_client.get_table.side_effect = NotFound("Table not found")

    # --- 2. Run Function ---
    # Mock 'os.path.exists' so it finds the fake config file
    with patch("os.path.exists", return_value=True):
        # Mock opening the file
        with patch("builtins.open", mock_open(read_data='[]')):
            # Mock json.load to return a valid schema list
            with patch("json.load", return_value=[{"name": "col1", "type": "STRING"}]):
                 create_table_managed()

    # --- 3. Assertions ---
    # Verify create_table was actually called
    mock_client.create_table.assert_called_once()
    
    # Verify the script did NOT exit (which would happen on failure)
    mock_sys_exit.assert_not_called()