# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=wsgi.py

# Install system dependencies for XGBoost and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
# Use robust pip flags to handle unstable connections
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --default-timeout=1000 --retries 10 --prefer-binary -r requirements.txt

# Copy the entire project
COPY . .

# Set PYTHONPATH to include the project root for src.models imports
ENV PYTHONPATH="/app:/app/web_app"

# The working directory for the app code is web_app
WORKDIR /app/web_app

# Default command (will be overridden by docker-compose)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
