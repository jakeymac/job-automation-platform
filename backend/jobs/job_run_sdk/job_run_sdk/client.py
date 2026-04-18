import logging
import os
import re
import unicodedata

import requests

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
JOB_ID = os.getenv("JOB_ID")
JOB_RUN_ID = os.getenv("RUN_ID")
JOB_RUN_API_URL = os.getenv("JOB_API_URL")

MAX_EMAIL_LENGTH = 5000


def form_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


def get_job_state():
    url = f"{JOB_RUN_API_URL}/runs/get_job_state/{JOB_RUN_ID}/"
    headers = form_headers()
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def set_job_run_state(updated_values):
    url = f"{JOB_RUN_API_URL}/runs/set_run_state/{JOB_RUN_ID}/"
    headers = form_headers()
    response = requests.post(url, json=updated_values, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def _sanitize_email_content(content):
    if not isinstance(content, str):
        content = str(content)
    # Fix broken encoding safely
    content = content.encode("utf-8", "replace").decode("utf-8")
    # Normalize unicode
    content = unicodedata.normalize("NFKC", content)
    # Remove control characters (but keep newlines)
    content = re.sub(r"[\x00-\x08\x0B-\x1F\x7F]", "", content)
    # Clean up whitespace
    content = re.sub(r"\n{3,}", "\n\n", content).strip()
    # Enforce max length
    if len(content) > MAX_EMAIL_LENGTH:
        content = content[:MAX_EMAIL_LENGTH] + "\n\n... (truncated)"
    if not content:
        return "Job completed but produced no readable output."

    return content


def set_job_run_email_content(email_content):
    url = f"{JOB_RUN_API_URL}/runs/set_run_email_content/{JOB_RUN_ID}/"
    headers = form_headers()
    sanitized_content = _sanitize_email_content(email_content)
    response = requests.post(
        url,
        json={"custom_email_content": sanitized_content},
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

    return response.json()
