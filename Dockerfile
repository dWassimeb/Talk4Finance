# Talk4Finance Production Dockerfile - Optimized
# Place this file as: Dockerfile (in root directory)

# Multi-stage build for frontend (if exists)
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend

# Handle frontend build or create placeholder
COPY frontend/package*.json ./
RUN if [ -f package.json ]; then \
      npm ci --only=production --silent; \
    else \
      mkdir -p build && echo "No frontend found, creating placeholder"; \
    fi

COPY frontend/ ./
RUN if [ -f package.json ]; then \
      npm run build; \
    else \
      mkdir -p build && \
      echo '<!DOCTYPE html><html><head><title>Talk4Finance</title></head><body><h1>Talk4Finance API</h1><p>FastAPI Backend Running</p><p><a href="/docs">API Documentation</a></p></body></html>' > build/index.html; \
    fi

# Python backend stage
FROM python:3.11-slim

# Build arguments
ARG GPT_API_KEY
ENV GPT_API_KEY=${GPT_API_KEY}

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the backend application (maintaining the app/ structure)
COPY backend/ ./

# Copy frontend build to serve static files
COPY --from=frontend-build /app/frontend/build ./static

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check using FastAPI health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Production-optimized startup command
# Using python3 -m uvicorn like your development setup, but with production settings
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]