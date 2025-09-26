# Use official Python image
FROM python:3.13-slim

WORKDIR /app

# Install system deps (if any needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run expects the server to listen on $PORT
ENV PORT=8080

# Gunicorn entrypoint (single process, as Cloud Run scales containers)
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
