# Use official Python image
FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr (important for logs)
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    docker.io
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . /app/

# Create directories for media and logs
RUN mkdir -p /app/media /app/logs

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose for worker)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
