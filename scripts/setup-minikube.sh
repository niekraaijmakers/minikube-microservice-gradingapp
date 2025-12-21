#!/bin/bash
# ==============================================================================
# Setup Minikube Cluster
# ==============================================================================
# This script sets up a minikube cluster with the necessary addons for
# demonstrating Kubernetes Ingress and Egress (NetworkPolicies).
#
# Prerequisites:
#   - minikube installed (brew install minikube)
#   - Docker Desktop running
#   - kubectl installed (brew install kubectl)
# ==============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Setting up Minikube Cluster                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    echo "❌ minikube not found. Install with: brew install minikube"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Install with: brew install kubectl"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ docker not found. Please install Docker Desktop"
    exit 1
fi

echo "✅ All prerequisites found"
echo ""

# Stop existing minikube if running
echo "🛑 Stopping any existing minikube cluster..."
minikube stop 2>/dev/null || true
minikube delete 2>/dev/null || true
echo ""

# Start minikube with Calico CNI for NetworkPolicy support
echo "🚀 Starting minikube with Calico CNI..."
echo "   (Calico is required for NetworkPolicy enforcement)"
echo ""

minikube start \
    --driver=docker \
    --cpus=4 \
    --memory=4096 \
    --cni=calico \
    --kubernetes-version=stable

echo ""
echo "⏳ Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=120s

echo ""
echo "🔌 Enabling required addons..."

# Enable ingress addon (nginx-ingress-controller)
echo "   → Enabling ingress addon..."
minikube addons enable ingress

# Enable metrics-server (optional, for monitoring)
echo "   → Enabling metrics-server..."
minikube addons enable metrics-server

echo ""
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=120s

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Minikube Setup Complete! ✅                    ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                             ║"
echo "║  Cluster info:                                              ║"
echo "║    $ kubectl cluster-info                                   ║"
echo "║                                                             ║"
echo "║  Next steps:                                                ║"
echo "║    1. Build images:  ./scripts/build-images.sh              ║"
echo "║    2. Deploy:        ./scripts/deploy.sh                    ║"
echo "║                                                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Show cluster info
echo "📊 Cluster Info:"
kubectl cluster-info
echo ""

# Show nodes
echo "📋 Nodes:"
kubectl get nodes
echo ""

