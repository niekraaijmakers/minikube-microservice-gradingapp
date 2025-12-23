#!/bin/bash
# ==============================================================================
# Build Docker Images inside Minikube
# ==============================================================================
# This script builds the Docker images directly inside the minikube VM,
# so they're available to Kubernetes without needing a registry.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Building Docker Images in Minikube                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Start it first with: ./scripts/setup-minikube.sh"
    exit 1
fi

# Configure shell to use minikube's Docker daemon
echo "🔧 Configuring Docker to use minikube's daemon..."
eval $(minikube docker-env)
echo "✅ Docker configured"
echo ""

# Build student-service
echo "📦 Building student-service..."
docker build -t student-service:latest "$PROJECT_ROOT/services/student-service"
echo "✅ student-service built"
echo ""

# Build grade-service
echo "📦 Building grade-service..."
docker build -t grade-service:latest "$PROJECT_ROOT/services/grade-service"
echo "✅ grade-service built"
echo ""

# Build frontend
echo "📦 Building frontend..."
docker build -t frontend:latest "$PROJECT_ROOT/services/frontend"
echo "✅ frontend built"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Images Built Successfully! ✅                  ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                             ║"
echo "║  Images available in minikube:                              ║"
echo "║    - student-service:latest                                 ║"
echo "║    - grade-service:latest                                   ║"
echo "║    - frontend:latest                                        ║"
echo "║                                                             ║"
echo "║  Next step:                                                 ║"
echo "║    Deploy to Kubernetes: ./scripts/deploy.sh                ║"
echo "║                                                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# List images
echo "📋 Docker images in minikube:"
docker images | grep -E "(student-service|grade-service|frontend|REPOSITORY)"
echo ""

