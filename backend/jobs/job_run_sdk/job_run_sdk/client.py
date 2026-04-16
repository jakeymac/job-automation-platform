import os

import requests
import logging

logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("API_TOKEN")
JOB_RUN_ID = os.getenv("RUN_ID")
JOB_RUN_API_URL = os.getenv("JOB_API_URL")


def form_headers():
    return {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }


def set_job_run_state(updated_values):
    url = f"{JOB_RUN_API_URL}/runs/set_run_state/{JOB_RUN_ID}/"
    headers = form_headers()
    response = requests.post(url, json=updated_values, headers=headers)
    response.raise_for_status()
    return response.json()


def _sanitize_email_content(content):
    if not content:
        return "No content provided"
    
    try:
        content = content.encode("utf-8", "replace").decode("utf-8")
    except Exception as e:
        logger.error(f"Error encoding email content: {e}")
        content = str(content)

    content = content.replace("\x00", "")
    return content

def set_job_run_email_content(email_content):
    url = f"{JOB_RUN_API_URL}/runs/set_run_email_content/{JOB_RUN_ID}/"
    headers = form_headers()
    sanitized_content = _sanitize_email_content(email_content)
    response = requests.post(
        url, json={"custom_email_content": sanitized_content}, headers=headers
    )
    response.raise_for_status()
    
    return response.json()
