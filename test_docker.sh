#!/bin/bash

# Test script for Docker setup
# This script verifies that the Docker container works correctly

set -e

echo "🐳 Testing PR Reviewer Helper Docker Setup"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker is installed"

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo "❌ .env file not found. Please create it from env.template first."
    echo "Example:"
    echo "  cp env.template .env"
    echo "  # Edit .env with your GitHub credentials"
    exit 1
fi

echo "✅ .env file found"

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t local-pr-reviewer . > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Test basic functionality
echo "🧪 Testing basic functionality..."
docker run --rm \
    -v ~/.pr_reviewer_cache:/cache \
    -v $(pwd):/app/output \
    --env-file .env \
    -e PR_REVIEWER_CACHE_DIR=/cache \
    local-pr-reviewer \
    --help > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo "✅ Basic functionality test passed"
else
    echo "❌ Basic functionality test failed"
    exit 1
fi

# Test configuration loading
echo "🧪 Testing configuration loading..."
docker run --rm \
    -v ~/.pr_reviewer_cache:/cache \
    -v $(pwd):/app/output \
    --env-file .env \
    -e PR_REVIEWER_CACHE_DIR=/cache \
    local-pr-reviewer \
    python -c "from config import get_config; config = get_config(); print('✅ Configuration loaded successfully')" 2>/dev/null

if [[ $? -eq 0 ]]; then
    echo "✅ Configuration test passed"
else
    echo "❌ Configuration test failed"
    echo "Please check your .env file has all required variables:"
    echo "  - GITHUB_TOKEN"
    echo "  - GITHUB_USERNAME" 
    echo "  - GITHUB_REPOSITORY"
    exit 1
fi

echo ""
echo "🎉 All tests passed! Your Docker setup is ready."
echo ""
echo "You can now run the tool with:"
echo "  ./docker-run.sh --pr 123"
echo "  docker run --rm -v ~/.pr_reviewer_cache:/cache -v \$(pwd):/app/output --env-file .env local-pr-reviewer --pr 123" 