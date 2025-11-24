#!/bin/bash
set -e

# Set PostgreSQL password from environment or default
export PGPASSWORD=${POSTGRES_PASSWORD:-lms_pass}
POSTGRES_USER=${POSTGRES_USER:-lms_user}
POSTGRES_HOST=${POSTGRES_HOST:-postgres}

echo "Waiting for PostgreSQL to be ready..."
# Wait for PostgreSQL to accept connections
until pg_isready -h "$POSTGRES_HOST" -U "$POSTGRES_USER"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is ready!"

# Initialize database (run as appuser)
echo "Initializing database..."
su - appuser -c "cd /app && python check_and_init.py" || {
  echo "Warning: Database initialization failed, but continuing..."
}

# Start the application
echo "Starting API server..."
exec "$@"

