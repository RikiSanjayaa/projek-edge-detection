# Coin Classification API - Docker Image
# Uses TensorFlow for CNN inference

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OpenCV (headless)
RUN apt-get update && apt-get install -y --no-install-recommends \
  libglib2.0-0 \
  libsm6 \
  libxrender1 \
  libxext6 \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements-docker.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-docker.txt

# Copy application code
COPY api/ ./api/
COPY preprocessing.py .

# Copy models (will be overwritten by volume mount if needed)
COPY models/*.keras ./models/
COPY models/*.pkl ./models/

# Create __init__.py if not exists
RUN touch api/__init__.py

# Environment variables (can be overridden)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV CORS_ORIGINS=*

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the API
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
