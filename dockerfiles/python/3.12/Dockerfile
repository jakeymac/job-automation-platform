FROM python:3.12-slim

# Install your SDK
COPY backend/jobs/job_run_sdk/ /opt/job_run_sdk/
RUN pip install /opt/job_run_sdk

# Optional but nice
RUN apt-get update && apt-get install -y curl jq && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace