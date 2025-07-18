#!/bin/bash

# Exit on error
set -e

# Load version from pyproject.toml
CURRENT_VERSION=$(poetry version -s)
echo "Current version: $CURRENT_VERSION"

# Build Docker image
echo "Building Docker image..."
docker build -t langgen-api:${CURRENT_VERSION} -t langgen-api:latest .

# Generate unique container name
TEST_CONTAINER_NAME="langgen-test-$(date +%s)"
echo "Testing container: $TEST_CONTAINER_NAME"

# Clean up any existing test container if it exists
if docker ps -a --filter "name=langgen-test" | grep -q langgen-test; then
    echo "Cleaning up old test containers..."
    docker rm -f $(docker ps -a --filter "name=langgen-test" -q) || true
fi

# Test the image with unique name
echo "Starting test container..."
docker run -d -p 8000:8000 --name $TEST_CONTAINER_NAME langgen-api:${CURRENT_VERSION}

# Wait for container to start
sleep 5

# Health check with retries
MAX_RETRIES=5
RETRY_DELAY=2
for i in $(seq 1 $MAX_RETRIES); do
    if curl -s http://localhost:8000/health | grep -q '"status":"healthy"'; then
        echo "Health check passed"
        HEALTH_CHECK_PASSED=true
        break
    else
        echo "Health check attempt $i failed"
        if [ $i -lt $MAX_RETRIES ]; then
            sleep $RETRY_DELAY
        fi
    fi
done

# Handle test results
if [ "$HEALTH_CHECK_PASSED" = true ]; then
    echo "Test successful, cleaning up..."
    docker stop $TEST_CONTAINER_NAME
    docker rm $TEST_CONTAINER_NAME
else
    echo "Health check failed after $MAX_RETRIES attempts"
    echo "Container logs:"
    docker logs $TEST_CONTAINER_NAME
    docker stop $TEST_CONTAINER_NAME
    docker rm $TEST_CONTAINER_NAME
    exit 1
fi

# Create GitHub release
echo "Creating GitHub release..."
git tag -a "v${CURRENT_VERSION}" -m "Release v${CURRENT_VERSION}"
git push origin "v${CURRENT_VERSION}"

echo "Release v${CURRENT_VERSION} completed successfully!"