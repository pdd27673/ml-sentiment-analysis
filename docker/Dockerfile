# Multi-stage Dockerfile for ML Model Service

# Builder stage - Install dependencies and download model
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application code needed for model download
COPY app/ ./app/
COPY scripts/ ./scripts/

# Pre-download the model to cache
RUN mkdir -p model_cache
RUN python scripts/download_model.py

# Final stage - Slim runtime image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code
COPY app/ ./app/
COPY scripts/ ./scripts/

# Copy pre-downloaded model cache
COPY --from=builder /app/model_cache ./model_cache

# Set PATH to include user packages
ENV PATH=/home/appuser/.local/bin:$PATH

# Change ownership to appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health')" || exit 1

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]