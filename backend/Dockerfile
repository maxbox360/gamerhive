# backend/Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for some packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Expose Django default port
EXPOSE 8000

# Default command
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
