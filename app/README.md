# 🐍 Python Workloads & Tools

This directory contains the core application logic of the Data Platform.
The scripts located here are designed to execute inside **Ephemeral Kubernetes Agents** spawned by Jenkins. They are stateless, configurable strictly via environment variables, and adhere to **Workload Identity** security practices (no long-lived keys).

---

## 📂 File Index

| File | Type | Description |
| :--- | :--- | :--- |
| `demo_pipeline.py` | **ETL Job** | A self-healing data ingestion script. It connects to BigQuery, checks if the infrastructure exists, and inserts a log row with build metadata. |
| `create_table.py` | **Infra Tool** | An idempotent utility to manage BigQuery schemas. It reads JSON definitions from `config/` and applies them to the cloud. |
| `requirements.txt` | **Config** | Python dependencies (pinned versions recommended for stability). |
| `config/` | **Schemas** | Directory containing JSON schema definitions used by `create_table.py`. |
| `tests/` | **QA** | Unit tests suite using `pytest` and mocks (see [tests/README.md](tests/README.md)). |

---

## ⚙️ Configuration (Environment Variables)

These scripts **do not accept command-line arguments**. They are configured strictly via Environment Variables injected by Jenkins (via `Jenkinsfile` or Global Properties).

### 1. Global Variables (Required for all scripts)
| Variable | Source | Description |
| :--- | :--- | :--- |
| `PROJECT_ID` | Jenkins Global Config | The GCP Project ID where BigQuery resides. **Critical:** Scripts will fail immediately if this is missing. |

### 2. Configuration for `demo_pipeline.py`
| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATASET_ID` | `jenkins_demo_db` | Target BigQuery Dataset. |
| `TABLE_ID` | `build_logs` | Target Table name. |
| `BUILD_NUMBER` | `DEV-1` | Injected automatically by Jenkins. Used to track data lineage (which build created this row). |

### 3. Configuration for `create_table.py`
| Variable | Required | Description |
| :--- | :--- | :--- |
| `DATASET_ID` | ✅ Yes | Target Dataset. |
| `TABLE_ID` | ✅ Yes | Target Table to create/update. |
| *Schema Path* | *Auto-calculated* | The script enforces a strict naming convention. It looks for `config/<DATASET_ID>_<TABLE_ID>.json`. |

---

## 🧠 Logical Flows & Behavior

### `demo_pipeline.py` (The Self-Healing Worker)
Designed for robustness in uncertain environments.
1.  **Auth:** Initializes `bigquery.Client` using the environment's credentials.
2.  **Check Dataset:** Tries to fetch the dataset. If `NotFound`, it creates it automatically.
3.  **Check Table:** Tries to fetch the table. If `NotFound`, creates it using a **Hardcoded Schema** (Build ID, Timestamp, Status) defined inside the script.
4.  **Insert:** Appends a JSON row to BigQuery.
5.  **Exit Code:** Returns `0` on success, `1` on failure (triggering Jenkins pipeline failure).

### `create_table.py` (The Infrastructure Tool)
Designed for Idempotency and Infrastructure-as-Code.
1.  **Validation:** Checks presence of all Env Vars.
2.  **Path Resolution:** dynamic resolution of the JSON schema path.
3.  **Idempotency Check:** Checks if the table already exists in BigQuery.
    * **If YES:** Prints "Already Exists" and exits gracefully with Code `0`. It does **not** overwrite data.
    * **If NO:** Reads the JSON file, parses fields, and calls `create_table`.
4.  **Error Handling:** Uses `sys.exit(1)` for any configuration error (missing file, bad JSON) to stop the pipeline immediately.

---

## 🔐 Authentication Guide

The code handles authentication transparently based on where it is running.

### A. Running in Jenkins (Production)
Authentication is handled by **GKE Workload Identity**.
* The Kubernetes Pod has a Service Account (`jenkins-sa`) mounted.
* The Google client library detects the token at `/var/run/secrets/...`.
* **Action required:** None. Just ensure `PROJECT_ID` is set correctly in Jenkins.

### B. Running Locally (Development)
To run these scripts on your laptop, you must provide your personal credentials via Application Default Credentials (ADC).

1.  **Login:**
    ```bash
    gcloud auth application-default login
    ```
2.  **Set Environment Variables:**
    ```bash
    export PROJECT_ID="your-project-id"
    export DATASET_ID="test_db"
    export TABLE_ID="test_table"
    ```
3.  **Run:**
    ```bash
    python demo_pipeline.py
    ```

---

## 📦 Dependencies & Setup

Dependencies are managed via `requirements.txt`.

**Installation:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---
## 🧪 Testing

We use **Pytest** with `unittest.mock` to ensure logic validity before deployment. The tests run automatically in the `Pull-Request-CI` pipeline.

```bash
# Run tests locally
pip install -r requirements.txt
pytest tests/ -v
```