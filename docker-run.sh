#!/bin/bash

# PR Reviewer Helper - Docker Runner Script
# This script makes it easy to run the tool in Docker

set -e

# Default values
CACHE_DIR="${HOME}/.pr_reviewer_cache"
OUTPUT_DIR="$(pwd)/reviews"
ENV_FILE=".env"

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] --pr <PR_NUMBER>"
    echo ""
    echo "Options:"
    echo "  --pr <NUMBER>              Pull request number (required)"
    echo "  --cache-dir <DIR>          Cache directory (default: ~/.pr_reviewer_cache)"
    echo "  --output-dir <DIR>         Output directory (default: ./reviews)"
    echo "  --env-file <FILE>          Environment file (default: .env)"
    echo "  --include-comments         Include PR comments"
    echo "  --include-review-comments  Include review comments"
    echo "  --skip-diff                Skip diff generation"
    echo "  --clean-cache              Clean cache before running"
    echo "  --help                     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --pr 123"
    echo "  $0 --pr 456 --output-dir ./reviews"
    echo "  $0 --pr 789 --include-comments --include-review-comments"
}

# Parse arguments
PR_NUMBER=""
DOCKER_ARGS=""
CUSTOM_CACHE_DIR=""
CUSTOM_OUTPUT_DIR=""
CUSTOM_ENV_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --pr)
            PR_NUMBER="$2"
            shift 2
            ;;
        --cache-dir)
            CUSTOM_CACHE_DIR="$2"
            shift 2
            ;;
        --output-dir)
            CUSTOM_OUTPUT_DIR="$2"
            shift 2
            ;;
        --env-file)
            CUSTOM_ENV_FILE="$2"
            shift 2
            ;;
        --include-comments)
            DOCKER_ARGS="$DOCKER_ARGS --include-comments"
            shift
            ;;
        --include-review-comments)
            DOCKER_ARGS="$DOCKER_ARGS --include-review-comments"
            shift
            ;;
        --skip-diff)
            DOCKER_ARGS="$DOCKER_ARGS --skip-diff"
            shift
            ;;
        --clean-cache)
            DOCKER_ARGS="$DOCKER_ARGS --clean-cache"
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if PR number is provided
if [[ -z "$PR_NUMBER" ]]; then
    echo "Error: PR number is required. Use --pr <NUMBER>"
    show_usage
    exit 1
fi

# Use custom values if provided
if [[ -n "$CUSTOM_CACHE_DIR" ]]; then
    CACHE_DIR="$CUSTOM_CACHE_DIR"
fi

if [[ -n "$CUSTOM_OUTPUT_DIR" ]]; then
    OUTPUT_DIR="$CUSTOM_OUTPUT_DIR"
fi

if [[ -n "$CUSTOM_ENV_FILE" ]]; then
    ENV_FILE="$CUSTOM_ENV_FILE"
fi

# Check if environment file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: Environment file '$ENV_FILE' not found."
    echo "Please create it from env.template and add your GitHub credentials."
    exit 1
fi

# Create cache directory if it doesn't exist
mkdir -p "$CACHE_DIR"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Build Docker image if it doesn't exist
if [[ "$(docker images -q local-pr-reviewer 2> /dev/null)" == "" ]]; then
    echo "Building Docker image..."
    docker build -t local-pr-reviewer .
fi

# Run the container
echo "Running PR Reviewer Helper for PR #$PR_NUMBER..."
docker run --rm \
    -v "$CACHE_DIR:/cache" \
    -v "$OUTPUT_DIR:/app/output" \
    --env-file "$ENV_FILE" \
    -e PR_REVIEWER_CACHE_DIR=/cache \
    local-pr-reviewer \
    --pr "$PR_NUMBER" \
    --output-dir /app/output \
    $DOCKER_ARGS

echo "Done! Check the output directory for the review file." 