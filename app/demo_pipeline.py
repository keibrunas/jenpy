import os
import datetime
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# comment to try the ci pipeline in jenkins
# comment comment comment comment comment

def run_demo():
    # 1. Get Config from Environment Variables
    # ✅ FIX: Use os.getenv with defaults so tests can override them
    PROJECT_ID = os.getenv("PROJECT_ID")
    DATASET_ID = os.getenv("DATASET_ID", "jenkins_demo_db")
    TABLE_ID = os.getenv("TABLE_ID", "build_logs")

    print(f"🚀 Connecting to BigQuery project: {PROJECT_ID}")

    # ✅ FIX: Initialize Client INSIDE the function
    # This allows the test to successfully mock 'bigquery.Client'
    client = bigquery.Client(project=PROJECT_ID)

    # 2. Create Dataset if not exists
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"✅ Dataset {DATASET_ID} exists.")
    except NotFound:  # ✅ Best Practice: Catch specific error
        print(f"📦 Creating Dataset {DATASET_ID}...")
        client.create_dataset(dataset_ref)

    # 3. Define Table Schema
    table_ref = dataset_ref.table(TABLE_ID)
    schema = [
        bigquery.SchemaField("build_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    ]

    # 4. Create Table if not exists
    try:
        client.get_table(table_ref)
        print(f"✅ Table {TABLE_ID} exists.")
    except NotFound:
        print(f"📄 Creating Table {TABLE_ID}...")
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)

    # 5. Insert a Row
    rows_to_insert = [
        {
            "build_id": os.environ.get("BUILD_NUMBER", "DEV-1"),
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "SUCCESS"
        }
    ]
    
    # Insert rows
    errors = client.insert_rows_json(table_ref, rows_to_insert)
    
    if errors:
        print(f"❌ Error inserting rows: {errors}")
        exit(1)
    else:
        print(f"🎉 Successfully inserted 1 row into {DATASET_ID}.{TABLE_ID}")

if __name__ == "__main__":
    run_demo()