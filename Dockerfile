FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Configure Git for better authentication handling
RUN git config --global credential.helper store && \
    git config --global init.defaultBranch main

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p /cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PR_REVIEWER_CACHE_DIR=/cache

# Create entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "--pr" ]; then\n\
    shift\n\
    python main.py "$@"\n\
else\n\
    python main.py "$@"\n\
fi' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"] 