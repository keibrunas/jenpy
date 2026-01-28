"""
Test unitari per il modulo app.create_table.
Verifica la creazione della tabella e la gestione del file di configurazione.
"""

from unittest.mock import MagicMock, patch, mock_open

# FIX: C0415 Import outside toplevel moved here
from google.api_core.exceptions import NotFound

from app.create_table import create_table_managed


# FIX: Patch the entire 'bigquery' module
@patch("app.create_table.bigquery")
# FIX: Patch 'sys.exit' to prevent the test from crashing
@patch("app.create_table.sys.exit")
@patch.dict(
    "os.environ",
    {"PROJECT_ID": "test-project", "DATASET_ID": "test_db", "TABLE_ID": "test_table"},
)
def test_create_table_success(mock_sys_exit, mock_bigquery):
    """
    Testa il percorso felice (happy path):
    - Configurazione trovata.
    - Tabella non esistente (NotFound).
    - Creazione tabella avvenuta con successo.
    """
    # --- 1. Setup Mocks ---
    mock_client = MagicMock()
    mock_bigquery.Client.return_value = mock_client

    # Handle the 'SchemaField.from_api_repr' call
    mock_bigquery.SchemaField.from_api_repr.side_effect = lambda x: x

    # Simulate that table does NOT exist (raises NotFound)
    mock_client.get_table.side_effect = NotFound("Table not found")

    # --- 2. Run Function ---
    # Mock 'os.path.exists' so it finds the fake config file
    with patch("os.path.exists", return_value=True):
        # Mock opening the file
        with patch("builtins.open", mock_open(read_data="[]")):
            # Mock json.load to return a valid schema list
            with patch("json.load", return_value=[{"name": "col1", "type": "STRING"}]):
                create_table_managed()

    # --- 3. Assertions ---
    # Verify create_table was actually called
    mock_client.create_table.assert_called_once()

    # Verify the script did NOT exit (which would happen on failure)
    mock_sys_exit.assert_not_called()
