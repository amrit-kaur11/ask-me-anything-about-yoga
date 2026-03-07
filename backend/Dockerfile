# Use official lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (avoid caching)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/storage/requirements.txt requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/app ./app
COPY backend/storage ./storage

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
