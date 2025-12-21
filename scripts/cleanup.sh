#!/bin/bash
# ==============================================================================
# Cleanup Script
# ==============================================================================
# Removes all deployed resources from the Kubernetes cluster.
# ==============================================================================

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Cleaning up Kubernetes Resources                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

read -p "⚠️  This will delete all resources in grading-system namespace. Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🗑️  Deleting namespace (and all resources within it)..."
kubectl delete namespace grading-system --ignore-not-found

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "To completely remove minikube cluster:"
echo "  minikube delete"
echo ""

