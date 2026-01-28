# 🐍 Application Logic

This directory contains the Python source code that runs inside the ephemeral Kubernetes Agents during pipeline execution. It implements the core Data Engineering logic (ETL) and Infrastructure management tools.

## 📂 File Structure

| File | Description |
| :--- | :--- |
| `demo_pipeline.py` | **ETL Workload.** Connects to BigQuery, ensures the dataset/table exists, and inserts a log row with the build status. |
| `create_table.py` | **Infra Tool.** Reads JSON schemas from `config/` and creates/updates BigQuery tables idempotently. |
| `tests/` | **Unit Tests.** Contains `pytest` logic to verify code behavior without connecting to real Cloud APIs (using Mocks). |
| `requirements.txt` | Python dependencies (google-cloud-bigquery, pytest, etc.). |

## 🧪 Testing

We use **Pytest** with `unittest.mock` to ensure logic validity before deployment. The tests run automatically in the `Pull-Request-CI` pipeline.

```bash
# Run tests locally
pip install -r requirements.txt
pytest tests/ -v

🔐 Authentication
The scripts do not use JSON keys. They rely on GKE Workload Identity. When running inside the cluster, the jenkins-sa Kubernetes Service Account injects the Google Cloud credentials automatically.

Local Development: Requires gcloud auth application-default login.

Production: Handled transparently by the Kubernetes Pod.

Certamente. Un README dettagliato per la cartella `app/` è fondamentale perché è il punto d'incontro tra lo sviluppatore Python (che scrive la logica) e il DevOps Engineer (che deve farla girare).

Ecco una versione espansa e "Deep Dive" del README per `app/`. Ho aggiunto sezioni specifiche sulle **Variabili d'Ambiente** (il contratto con Jenkins) e sui **flussi logici** dei singoli script, utile per chi deve fare debug.

---

### `app/README.md`

```markdown
# 🐍 Python Workloads & Tools

This directory contains the core logic of the Data Platform.
The scripts here are designed to run inside **Ephemeral Kubernetes Pods**, meaning they are stateless, configurable via environment variables, and rely on Workload Identity for authentication.

## 📂 File Index

| File | Type | Description |
| :--- | :--- | :--- |
| `demo_pipeline.py` | **ETL Job** | A sample data ingestion script. It connects to BigQuery, ensures the target schema exists, and appends a row with build metadata. |
| `create_table.py` | **Infra Tool** | An idempotent utility to manage BigQuery schemas. It reads JSON definitions and applies them to the cloud. |
| `requirements.txt` | **Config** | Python dependencies (pinned versions recommended for stability). |
| `tests/` | **QA** | Unit tests suite (see internal README). |
| `config/` | **Schemas** | (Optional) Folder containing JSON schema definitions for `create_table.py`. |

---

## ⚙️ Configuration (Environment Variables)

These scripts **do not accept command-line arguments**. They are configured strictly via Environment Variables injected by Jenkins.

### Global Variables
| Variable | Required | Source | Description |
| :--- | :--- | :--- | :--- |
| `PROJECT_ID` | ✅ Yes | Jenkins (`GlobalNodeProperties`) | The GCP Project ID where BigQuery resides. |

### For `demo_pipeline.py`
| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATASET_ID` | `jenkins_demo_db` | Target BigQuery Dataset. |
| `TABLE_ID` | `build_logs` | Target Table name. |
| `BUILD_NUMBER` | `DEV-1` | Injected automatically by Jenkins to track lineage. |

### For `create_table.py`
| Variable | Required | Description |
| :--- | :--- | :--- |
| `DATASET_ID` | ✅ Yes | Target Dataset. |
| `TABLE_ID` | ✅ Yes | Target Table to create/update. |
| *Schema File* | *Implied* | The script looks for `config/<DATASET_ID>_<TABLE_ID>.json`. |

---

## 🧠 Logical Flows

### 1. `demo_pipeline.py` (Self-Healing ETL)
This script is designed to be robust. It doesn't assume the infrastructure exists.
1.  **Auth:** Initializes `bigquery.Client` using the environment's credentials.
2.  **Check Dataset:** Tries to `get_dataset`. If `NotFound`, it creates it.
3.  **Check Table:** Tries to `get_table`. If `NotFound`, creates it with a **hardcoded schema** (Build ID, Timestamp, Status).
4.  **Insert:** Appends a JSON row to BigQuery.
5.  **Exit Code:** Returns `0` on success, `1` on failure (triggering Jenkins failure).

### 2. `create_table.py` (Infrastructure as Code)
This script enforces a strict naming convention for schema management.
1.  **Validation:** Checks if `PROJECT_ID`, `DATASET_ID`, and `TABLE_ID` are present.
2.  **Path Resolution:** Calculates the expected schema path: `config/{DATASET}_{TABLE}.json`.
3.  **Idempotency Check:** Checks if the table already exists in BigQuery.
    * **If YES:** Prints "Already Exists" and exits gracefully (Code 0). It does **not** overwrite data.
    * **If NO:** Reads the JSON file, parses fields, and calls `create_table`.

---

## 🔐 Authentication Guide

The code does not handle keys manually. It relies on the environment.

### A. Running in Jenkins (Production)
Authentication is handled by **GKE Workload Identity**.
The Kubernetes Pod has a Service Account (`jenkins-sa`) mounted. The Google client library detects this automatically.
* **Action required:** None. Just ensure `PROJECT_ID` is set.

### B. Running Locally (Development)
To run these scripts on your laptop, you must provide your personal credentials to the Application Default Credentials (ADC).

1.  **Login:**
    ```bash
    gcloud auth application-default login
    ```
2.  **Set Env Vars:**
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

## 📦 Dependencies

Managed via `pip`. To install for development:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

**Key Libraries:**

* `google-cloud-bigquery`: Interaction with GCP.
* `pytest` & `pytest-mock`: Testing framework.
