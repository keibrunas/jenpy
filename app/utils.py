"""
Shared utilities for the application.
Handles logging configuration and authentication logic.
"""

import logging
import os
import sys

import google.auth
import google.auth.exceptions


def setup_logging(name: str) -> logging.Logger:
    """
    Configures a non-buffered logger that outputs to stdout.
    Essential for Kubernetes environments.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers if re-imported
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_project_id() -> str:
    """
    Retrieves the Project ID.
    Priority:
    1. Environment Variable (Injected by Jenkins).
    2. Default Credentials (Workload Identity).

    Returns:
        str: The GCP Project ID.

    Raises:
        ValueError: If Project ID cannot be determined.
    """
    # 1. Check Environment Variable
    project_id = os.getenv("PROJECT_ID")
    if project_id:
        return project_id

    # 2. Check Workload Identity / Default Credentials
    try:
        _, project_id = google.auth.default()

        # FIX PER PYLANCE:
        # google.auth.default() può ritornare None come project_id.
        # Dobbiamo verificarlo esplicitamente.
        if not project_id:
            raise ValueError("GCP Credentials found, but no Project ID associated.")

        return project_id

    except google.auth.exceptions.DefaultCredentialsError as exc:
        raise ValueError("Missing Project ID and authentication failed.") from exc
