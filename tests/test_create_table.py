import pytest
from unittest.mock import MagicMock, patch, mock_open
from app.create_table import create_table_managed

@patch('app.create_table.bigquery.Client')
@patch.dict('os.environ', {
    'PROJECT_ID': 'test-project', 
    'DATASET_ID': 'test_db', 
    'TABLE_ID': 'test_table'
})
def test_create_table_success(mock_client_cls):
    # 1. Setup Mock
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    
    # Simulate that table does NOT exist (raises NotFound)
    from google.api_core.exceptions import NotFound
    mock_client.get_table.side_effect = NotFound("Table not found")

    # 2. Run Function
    # ✅ FIX: Use mock_open directly (removed pytest.mock_open)
    with patch("builtins.open", mock_open(read_data='[{"name": "col1", "type": "STRING"}]')):
        with patch("json.load", return_value=[{"name": "col1", "type": "STRING"}]):
             create_table_managed()

    # 3. Assertions
    mock_client.create_table.assert_called_once()