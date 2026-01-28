# 🛤️ Jenkins Pipelines

This directory contains the **Jenkinsfiles** that define our CI/CD automation logic.
Jenkins detects these files and automatically configures the jobs via Job DSL.

## 📋 Pipeline Catalog

### 1. `ci-pr-check.jenkinsfile`
* **Type:** Multibranch Pipeline.
* **Trigger:** Runs automatically on every Pull Request or commit to branches.
* **Tasks:**
    * Installs dependencies.
    * Runs Unit Tests (`pytest`).
    * **Optimization:** Uses the `when { changeset }` directive to only run tests if Python files have changed.

### 2. `demo-pipeline.jenkinsfile`
* **Type:** Standard Pipeline.
* **Purpose:** Runs the ETL workload (`demo_pipeline.py`).
* **Features:**
    * Injects `PROJECT_ID` environment variable.
    * Uses a dynamic Kubernetes Pod as the agent (defined inline).

### 3. `create-table.jenkinsfile`
* **Type:** Parameterized Pipeline.
* **Purpose:** Utility tool to create BigQuery tables on demand.
* **Inputs:**
    * `DATASET_ID`
    * `TABLE_ID`
* **Logic:** Passes user inputs to the `create_table.py` script to apply the Schema defined in the `config/` folder.

## 🤖 Dynamic Agents

All pipelines use **Ephemeral Kubernetes Agents**.
Instead of static build servers, every build:
1.  Spins up a new Pod in the cluster.
2.  Runs the steps inside the defined container (e.g., `python:3.11`).
3.  Destroys the Pod immediately after completion.

**Example Agent Definition:**
```groovy
agent {
    kubernetes {
        yaml """
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: python
            image: python:3.11-slim
            command: ['cat']
            tty: true
        """
    }
}