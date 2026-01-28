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