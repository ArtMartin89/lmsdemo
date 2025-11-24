# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Copy and setup entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user (but entrypoint runs as root to access pg_isready)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["su", "-", "appuser", "-c", "cd /app && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

