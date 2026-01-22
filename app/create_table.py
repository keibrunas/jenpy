import os
import sys
import json
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# comment to try the ci pipeline in jenkins
# new comments here

def create_table_managed():
    # 1. Capture Inputs
    project_id = os.getenv("PROJECT_ID")
    dataset_id = os.getenv("DATASET_ID")
    table_id = os.getenv("TABLE_ID")

    print(f"🚀 Job Started: Create Table")
    print(f"   Project: {project_id}")
    print(f"   Dataset: {dataset_id}")
    print(f"   Table:   {table_id}")

    if not all([project_id, dataset_id, table_id]):
        print("❌ Error: Missing required environment variables (DATASET_ID or TABLE_ID).")
        sys.exit(1)

    # ⚠️ NEW LOGIC: Construct Schema Path dynamically
    # Naming Convention: config/<dataset>_<table_name>.json
    schema_filename = f"{dataset_id}_{table_id}.json"
    schema_path = os.path.join("config", schema_filename)

    print(f"   Schema:  {schema_path}")

    # 2. CHECK: Does the table exist?
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    try:
        client.get_table(table_ref)
        print(f"⚠️  Table '{table_ref}' ALREADY EXISTS.")
        print("   Action: Graceful Exit (No changes made).")
        sys.exit(0)
    except NotFound:
        print(f"✨ Table not found. Proceeding to create it...")

    # 3. Load Schema from the Specific JSON File
    if not os.path.exists(schema_path):
        print(f"❌ Error: Configuration file not found!")
        print(f"   Expected file: {schema_path}")
        print(f"   Please create this file in the 'config/' folder to define your table.")
        sys.exit(1)

    try:
        with open(schema_path, "r") as f:
            schema_json = json.load(f)
            schema = [bigquery.SchemaField.from_api_repr(field) for field in schema_json]
    except json.JSONDecodeError as e:
        print(f"❌ Error: Failed to parse JSON in {schema_path}: {e}")
        sys.exit(1)

    # 4. CREATE the Table
    table = bigquery.Table(table_ref, schema=schema)
    try:
        created_table = client.create_table(table)
        print(f"✅ SUCCESS: Created table {created_table.full_table_id}")
    except Exception as e:
        print(f"❌ Failed to create table: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_table_managed()