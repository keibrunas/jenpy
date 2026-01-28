"""
Pipeline dimostrativa per l'inserimento di dati in BigQuery.
Simula un flusso CI/CD che scrive log di build.
"""

import os
import sys
import datetime
from google.cloud import bigquery
from google.api_core.exceptions import NotFound


def run_demo():
    """
    Esegue la logica della demo:
    1. Connette a BigQuery.
    2. Crea Dataset e Tabella se mancanti.
    3. Inserisce una riga di log.
    """
    # 1. Get Config from Environment Variables
    # FIX: C0103 Variable names should be lowercase inside functions
    project_id = os.getenv("PROJECT_ID")
    dataset_id = os.getenv("DATASET_ID", "jenkins_demo_db")
    table_id = os.getenv("TABLE_ID", "build_logs")

    print(f"🚀 Connecting to BigQuery project: {project_id}")

    # This allows the test to successfully mock 'bigquery.Client'
    client = bigquery.Client(project=project_id)

    # 2. Create Dataset if not exists
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {dataset_id} exists.")
    except NotFound:
        print(f"📦 Creating Dataset {dataset_id}...")
        client.create_dataset(dataset_ref)

    # 3. Define Table Schema
    table_ref = dataset_ref.table(table_id)
    schema = [
        bigquery.SchemaField("build_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    ]

    # 4. Create Table if not exists
    try:
        client.get_table(table_ref)
        print(f"✅ Table {table_id} exists.")
    except NotFound:
        print(f"📄 Creating Table {table_id}...")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

    # 5. Insert a Row
    rows_to_insert = [
        {
            "build_id": os.environ.get("BUILD_NUMBER", "DEV-1"),
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "SUCCESS",
        }
    ]

    # Insert rows
    errors = client.insert_rows_json(table_ref, rows_to_insert)

    if errors:
        print(f"❌ Error inserting rows: {errors}")
        sys.exit(1)  # FIX: R1722 Use sys.exit instead of exit()
    else:
        print(f"🎉 Successfully inserted 1 row into {dataset_id}.{table_id}")


if __name__ == "__main__":
    run_demo()
