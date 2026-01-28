# 🧪 Unit Testing Suite

This directory contains the automated tests for the Python application logic.
The suite uses **Pytest** and **unittest.mock** to verify the code logic in complete isolation, meaning **no real connection to Google Cloud is established**.

## 🎯 Philosophy

* **Fast:** Tests run in milliseconds.
* **Cost-Free:** No API calls are made to BigQuery.
* **Secure:** No Service Account keys or authentication are required to run these tests.

## 📂 File Index

| File | Description |
| :--- | :--- |
| `conftest.py` | **Configuration.** Sets up the Python path so tests can import modules from the parent `app/` directory without errors. |
| `test_create_table.py` | **Infra Logic.** Verifies that the table creation tool correctly reads JSON schemas and handles "Table Exists" scenarios gracefully. |
| `test_demo_pipeline.py` | **ETL Logic.** Simulates the data ingestion flow (Dataset check → Table check → Insert Row) confirming calls are made in the right order. |

## 🚀 How to Run

### Prerequisites
Make sure you have installed the dependencies:
```bash
pip install -r requirements.txt

```

### Running the Suite

Execute all tests with verbose output:

```bash
pytest tests/ -v

```

### Running Specific Tests

You can filter tests by name using the `-k` (keyword) flag:

```bash
# Run only tests related to the "demo" pipeline
pytest -k "demo" -v

```

## 🛠 Technical Deep Dive

### 1. The `conftest.py`

Since our folder structure separates `app/` and `tests/`, Python cannot naturally find the source code.
The `conftest.py` file automatically appends the project root to `sys.path` before any test runs.

### 2. Mocking Strategy

We use two main techniques to simulate Google Cloud:

* **`@patch` (The Interceptor):** We use decorators to intercept libraries like `google.cloud.bigquery` or `os.environ`.
* *Example:* `@patch('app.create_table.bigquery')` ensures that when the app tries to import BigQuery, it gets a fake object instead.


* **`MagicMock` (The Stuntman):** We create fake client objects that record how they are used.
* *Example:* We check `mock_client.create_table.assert_called_once()` to verify the code *tried* to create a table, without actually doing it.



### 3. Handling `sys.exit()`

The script `create_table.py` uses `sys.exit(1)` on failure. In a test environment, this would crash the test runner.
We patch `sys.exit` so that instead of quitting, it just records that "exit was called".

## 🤖 CI Integration

These tests are automatically executed in the **Pull Request Pipeline** (`ci-pr-check.jenkinsfile`).
Jenkins mounts the source code, installs dependencies, and runs `pytest`. If any test fails, the Pull Request is marked as failed.
