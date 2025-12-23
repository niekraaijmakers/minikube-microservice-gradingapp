#!/bin/bash
# ==============================================================================
# Deploy to Kubernetes
# ==============================================================================
# This script deploys all services, ingress, and network policies to the
# Kubernetes cluster.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
K8S_DIR="$PROJECT_ROOT/k8s"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Deploying to Kubernetes                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster."
    echo "   Make sure minikube is running: minikube status"
    exit 1
fi

echo "📁 Deploying from: $K8S_DIR"
echo ""

# Create namespaces
echo "📦 Creating namespaces..."
kubectl apply -f "$K8S_DIR/namespace.yaml"
echo ""

# Deploy services (ClusterIP)
echo "🔌 Creating services..."
kubectl apply -f "$K8S_DIR/services/"
echo ""

# Deploy deployments
echo "🚀 Creating deployments..."
kubectl apply -f "$K8S_DIR/deployments/"
echo ""

# Wait for pods to be ready
echo "⏳ Waiting for pods to be ready..."
kubectl wait --namespace grading-system \
    --for=condition=ready pod \
    --selector=app=student-service \
    --timeout=120s

kubectl wait --namespace grading-system \
    --for=condition=ready pod \
    --selector=app=grade-service \
    --timeout=120s

kubectl wait --namespace grading-system \
    --for=condition=ready pod \
    --selector=app=frontend \
    --timeout=120s

echo "✅ All pods are ready"
echo ""

# Deploy ingress
echo "🌐 Creating ingress..."
kubectl apply -f "$K8S_DIR/ingress/"
echo ""

# Ask about network policies
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Network Policies                                           ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║  Network policies restrict traffic between pods.            ║"
echo "║                                                             ║"
echo "║  Policies control:                                          ║"
echo "║  - Which pods can communicate with each other               ║"
echo "║  - External egress (internet access)                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

read -p "Apply network policies now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔒 Applying network policies..."
    kubectl apply -f "$K8S_DIR/network-policies/"
    echo ""
    echo "✅ Network policies applied"
else
    echo "⏭️  Skipping network policies (all traffic allowed)"
    echo "    Apply them later with: kubectl apply -f $K8S_DIR/network-policies/"
fi
echo ""

# Get minikube IP
MINIKUBE_IP=$(minikube ip)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Deployment Complete! ✅                        ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                             ║"
echo "║  To access the application:                                 ║"
echo "║                                                             ║"
echo "║  Option 1: Add to /etc/hosts and use ingress:               ║"
echo "║    echo \"$MINIKUBE_IP grading.local\" | sudo tee -a /etc/hosts"
echo "║    Then visit: http://grading.local                         ║"
echo "║                                                             ║"
echo "║  Option 2: Use minikube tunnel:                             ║"
echo "║    minikube tunnel                                          ║"
echo "║    Then visit: http://localhost                             ║"
echo "║                                                             ║"
echo "║  Option 3: Port-forward directly:                           ║"
echo "║    kubectl port-forward svc/frontend 8080:5000 -n grading-system"
echo "║    Then visit: http://localhost:8080                        ║"
echo "║                                                             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Show resources
echo "📊 Deployed Resources:"
echo ""
echo "Pods:"
kubectl get pods -n grading-system
echo ""
echo "Services:"
kubectl get svc -n grading-system
echo ""
echo "Ingress:"
kubectl get ingress -n grading-system
echo ""
echo "Network Policies:"
kubectl get networkpolicies -n grading-system
echo ""

