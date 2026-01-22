import pytest
from unittest.mock import MagicMock, patch
# Import the main function from your script
# Note: Ensure your demo-pipeline.py has a main() function or similar structure
from app.demo_pipeline import run_demo 

@patch('app.demo_pipeline.bigquery.Client')
def test_run_demo_success(mock_client_cls):
    # 1. Setup the Mock (The "Fake" BigQuery)
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    # Simulate that the dataset does NOT exist (raises NotFound), so code tries to create it
    from google.api_core.exceptions import NotFound
    mock_client.get_dataset.side_effect = NotFound("Dataset not found")
    
    # 2. Run the actual script function
    run_demo()

    # 3. Assertions (Did the script do what we expected?)
    # Check if it tried to create a dataset
    mock_client.create_dataset.assert_called()
    # Check if it tried to insert rows
    mock_client.insert_rows_json.assert_called()