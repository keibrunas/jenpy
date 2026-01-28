"""
Test unitari per il modulo app.demo_pipeline.
Verifica la logica di connessione, creazione dataset/tabella e inserimento righe.
"""

from unittest.mock import MagicMock, patch

# FIX: C0415 Import outside toplevel moved here
from google.api_core.exceptions import NotFound

from app.demo_pipeline import run_demo


# Patch the Client where it is imported in the app
@patch("app.demo_pipeline.bigquery.Client")
@patch.dict(
    "os.environ",
    {
        "PROJECT_ID": "test-project",
        "DATASET_ID": "test_dataset",
        "TABLE_ID": "test_table",
    },
)
def test_run_demo_success(mock_client_cls):
    """
    Testa il flusso completo di run_demo:
    - Dataset mancante -> creato.
    - Tabella mancante -> creata.
    - Inserimento righe -> successo.
    """
    # --- 1. Setup the Mock ---
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    # Simulate: Dataset NOT found (triggering creation)
    mock_client.get_dataset.side_effect = NotFound("Dataset not found")

    # Simulate: Table NOT found (triggering creation)
    mock_client.get_table.side_effect = NotFound("Table not found")

    # Simulate: Insert rows success (return empty list = no errors)
    mock_client.insert_rows_json.return_value = []

    # --- 2. Run the Function ---
    run_demo()

    # --- 3. Assertions ---
    # Verify we tried to create the dataset
    mock_client.create_dataset.assert_called_once()

    # Verify we tried to create the table
    mock_client.create_table.assert_called_once()

    # Verify we tried to insert rows
    mock_client.insert_rows_json.assert_called_once()
