"""
Module for automated table creation on BigQuery.
Designed for execution within Kubernetes/Jenkins environments.
"""

import json
import os
import sys
from pathlib import Path

from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Import shared utilities to avoid code duplication
from app.utils import setup_logging, get_project_id

# --- Logging Configuration ---
LOGGER = setup_logging("create_table_worker")


def load_schema(schema_path: Path) -> list[bigquery.SchemaField]:
    """
    Loads the JSON schema from the file system.

    Args:
        schema_path (Path): The path to the JSON schema file.

    Returns:
        list[bigquery.SchemaField]: The list of BigQuery fields.
    """
    if not schema_path.exists():
        LOGGER.error("❌ Missing schema file: %s", schema_path)
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    with schema_path.open("r", encoding="utf-8") as file_obj:
        schema_json = json.load(file_obj)
        return [bigquery.SchemaField.from_api_repr(field) for field in schema_json]


def create_table_logic(client: bigquery.Client, dataset_id: str, table_id: str) -> None:
    """
    Core logic for table creation.

    Args:
        client (bigquery.Client): Authenticated BigQuery client.
        dataset_id (str): Target Dataset ID.
        table_id (str): Target Table ID.
    """
    full_table_id = f"{client.project}.{dataset_id}.{table_id}"
    LOGGER.info("🚀 Starting Job for: %s", full_table_id)

    # Dynamic path construction based on convention
    schema_filename = f"{dataset_id}_{table_id}.json"
    schema_path = Path("config") / schema_filename
    LOGGER.info("   Schema Path: %s", schema_path)

    # 1. Check Table existence
    try:
        client.get_table(full_table_id)
        LOGGER.info("✅ Table '%s' already exists. No action taken.", full_table_id)
        return
    except NotFound:
        LOGGER.info("✨ Table not found. Proceeding with creation...")

    # 2. Load Schema and Create Table
    schema = load_schema(schema_path)
    table = bigquery.Table(full_table_id, schema=schema)
    created_table = client.create_table(table)
    LOGGER.info("🎉 SUCCESS: Created table %s", created_table.full_table_id)


def main() -> None:
    """Script entry point."""
    dataset_id = os.getenv("DATASET_ID")
    table_id = os.getenv("TABLE_ID")

    if not all([dataset_id, table_id]):
        LOGGER.error("❌ Missing environment variables: DATASET_ID or TABLE_ID")
        sys.exit(1)

    try:
        project_id = get_project_id()
        # Log explicitly here since get_project_id logic was moved
        LOGGER.info("ℹ️ Project ID resolved: %s", project_id)

        bq_client = bigquery.Client(project=project_id)
        create_table_logic(bq_client, dataset_id, table_id)  # type: ignore
    except Exception as exc:  # pylint: disable=broad-exception-caught
        LOGGER.exception("❌ Critical error during execution: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
