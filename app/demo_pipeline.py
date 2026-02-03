"""
Demo pipeline for inserting data into BigQuery.
Optimized for Container execution (UTC timestamps, Logging) and Testability.
"""
#commento

import datetime
import os
import sys
from typing import Any

from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Import shared utilities
from app.utils import setup_logging, get_project_id

# --- Logging Configuration ---
LOGGER = setup_logging("demo_pipeline")


def ensure_dataset(
    client: bigquery.Client, dataset_id: str
) -> bigquery.DatasetReference:
    """Checks and creates the dataset if missing (Idempotent)."""
    # FIX: Sostituiamo client.dataset() (Deprecato) con il costruttore diretto
    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)

    try:
        client.get_dataset(dataset_ref)
        LOGGER.info("✅ Dataset exists: %s", dataset_id)
    except NotFound:
        LOGGER.info("📦 Creating Dataset: %s", dataset_id)
        client.create_dataset(dataset_ref)
    return dataset_ref


def ensure_table(client: bigquery.Client, table_ref: bigquery.TableReference) -> None:
    """Checks and creates the table if missing using a hardcoded schema."""
    try:
        client.get_table(table_ref)
        LOGGER.info("✅ Table exists: %s", table_ref.table_id)
    except NotFound:
        LOGGER.info("📄 Creating Table: %s", table_ref.table_id)
        schema = [
            bigquery.SchemaField("build_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        ]
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)


def insert_build_log(
    client: bigquery.Client, table_ref: bigquery.TableReference, build_id: str
) -> None:
    """Prepares and executes the insertion of a log row."""
    timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

    row: dict[str, Any] = {
        "build_id": build_id,
        "timestamp": timestamp_utc,
        "status": "SUCCESS",
    }

    LOGGER.info("📤 Inserting row: %s", row)
    errors = client.insert_rows_json(table_ref, [row])

    if errors:
        LOGGER.error("❌ Insert errors: %s", errors)
        raise RuntimeError(f"BigQuery Insert Errors: {errors}")

    LOGGER.info("🎉 Pipeline completed successfully.")


def run_pipeline(
    project_id: str, dataset_id: str, table_id: str, build_number: str
) -> None:
    """Orchestrates the pipeline execution logic."""
    LOGGER.info("🚀 Start Pipeline. Project: %s | Build: %s", project_id, build_number)

    client = bigquery.Client(project=project_id)

    # 1. Infrastructure
    dataset_ref = ensure_dataset(client, dataset_id)
    table_ref = dataset_ref.table(table_id)
    ensure_table(client, table_ref)

    # 2. Data Insertion
    insert_build_log(client, table_ref, build_number)


def main() -> None:
    """Entry point. Handles environment variables and top-level error catching."""
    project_id = get_project_id()
    dataset_id = os.getenv("DATASET_ID", "jenkins_demo_db")
    table_id = os.getenv("TABLE_ID", "build_logs")
    build_number = os.getenv("BUILD_NUMBER", "LOCAL-DEV")

    if not project_id:
        LOGGER.error("❌ Critical: PROJECT_ID environment variable is missing.")
        sys.exit(1)

    try:
        run_pipeline(project_id, dataset_id, table_id, build_number)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        LOGGER.exception("❌ Fatal pipeline error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
