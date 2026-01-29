# 🧪 Unit Testing Suite

This directory contains the automated tests for the Python application logic (`app/`).
The suite uses **Pytest**, **pytest-cov**, and **unittest.mock** to verify code correctness in complete isolation, ensuring **100% Code Coverage** without any external dependencies.

## 🎯 Philosophy

* **Isolated:** No real connection to Google Cloud is established. We mock everything.
* **Fast:** Tests run in milliseconds, not seconds.
* **Secure:** No Service Account keys or authentication are required.
* **Strict:** We aim for 100% coverage to satisfy Pylance and Pylint requirements.

## 📂 File Index

| File | Description |
| --- | --- |
| `conftest.py` | **Configuration.** Sets up the Python path and provides the `clean_env` fixture to ensure test isolation (clears env vars between tests). |
| `test_utils.py` | **Core Logic.** Verifies shared utilities (`app.utils`), including idempotent logging setup and robust **Workload Identity** authentication fallback. |
| `test_create_table.py` | **Infra Logic.** Tests the table creation workflow, including JSON schema parsing and graceful handling of existing tables. |
| `test_demo_pipeline.py` | **ETL Logic.** Simulates the full data pipeline (Dataset → Table → Insert), ensuring correct call order and UTC timestamp generation. |

## 🚀 How to Run

### Prerequisites

Install the development dependencies (including `pytest-cov`):

```bash
pip install -r requirements-dev.txt

```

### Running the Suite (Standard)

Execute all tests with verbose output:

```bash
pytest tests/ -v

```

### Checking Code Coverage 🛡️

To verify the **100% coverage** goal, run with the coverage flags:

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=100 tests/

```

* `--cov=app`: Measures coverage only for the source code.
* `--cov-report=term-missing`: Shows exactly which lines are not covered in the terminal.
* `--cov-fail-under=100`: Forces the command to fail if coverage is not perfect.

## 🛠 Technical Deep Dive

### 1. Modular Architecture & Utils

We extracted common logic into `app.utils`. Consequently, we added `test_utils.py` to rigorously test:

* **Logging Idempotency:** Ensuring handlers are not duplicated if `setup_logging` is called multiple times.
* **Auth Fallbacks:** Testing the priority chain (Env Var → Workload Identity → Error).
* **Type Narrowing:** Specifically ensuring `ValueError` is raised if Google Auth returns `None` for the Project ID, satisfying strict **Pylance** checks.

### 2. Advanced Mocking Strategy

We use `unittest.mock` to simulate the Google Cloud environment.

* **The `Client` & `DatasetReference` Fix:**
Since the code now uses `bigquery.DatasetReference(client.project, dataset_id)`, our mocks must be precise. We explicitly set the project attribute on mock objects to avoid `ValueError` from the library:
```python
mock_client = MagicMock()
mock_client.project = "test-project" # Critical for DatasetReference validation

```


* **`@patch` Decorators:**
We patch imports where they are *used*, not where they are defined. For example, we patch `app.create_table.get_project_id` even though the function is defined in `utils`, ensuring the module under test receives the mock.

### 3. Main Entry Point Testing

To achieve 100% coverage, we encapsulate the script execution in a `main()` function. We test it by mocking `sys.exit` to prevent the test runner from aborting:

```python
@patch("app.demo_pipeline.sys.exit")
def test_main_failure(mock_exit):
    ...
    mock_exit.assert_called_with(1)

```

## 🤖 CI Integration

These tests are executed automatically in the **[Pull Request Pipeline](https://www.google.com/search?q=/pipelines/ci-pr-check.jenkinsfile)**.
The build enforces strict Quality Gates:

1. **Black:** Code formatting.
2. **Pylint:** Must score **> 9.0/10**.
3. **Coverage:** Must be **> 90%** (The pipeline allows a small margin, but local dev targets 100%).