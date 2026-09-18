# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for instant log flushing and clean execution
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server code
COPY server/ /app/server/
# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port (Render defaults to 10000, docker-compose uses 8000)
EXPOSE 8000 10000

# Run uvicorn using the PORT environment variable (required by Render)
CMD ["sh", "-c", "python -m uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
