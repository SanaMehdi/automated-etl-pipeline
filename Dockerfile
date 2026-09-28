FROM python:3.11-slim

# Prevent Python from creating .pyc files
# and ensure logs appear immediately.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first for Docker layer caching.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and configuration.
COPY src/ ./src/
COPY sql/ ./sql/
COPY data/raw/ ./data/raw/
COPY main.py .
COPY pytest.ini .

# Create runtime directories.
RUN mkdir -p /app/data/processed \
    /app/logs \
    /app/reports

# Default: run incremental ETL.
CMD ["python", "main.py", "--mode", "incremental"]
