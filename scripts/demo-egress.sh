#!/bin/bash
# ==============================================================================
# Egress Network Policy Demonstration
# ==============================================================================
# This script demonstrates how NetworkPolicies control EGRESS (outbound) traffic.
#
# The demo tests whether pods can reach external URLs like httpbin.org
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
K8S_DIR="$(dirname "$SCRIPT_DIR")/k8s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           EGRESS NETWORK POLICY DEMONSTRATION                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "This demo shows how NetworkPolicies control EGRESS (outbound) traffic."
echo ""
echo "We'll test if pods can reach external URLs like httpbin.org"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check if services are running
echo "🔍 Checking services..."
if ! kubectl get pods -n grading-system -l app=grade-service 2>/dev/null | grep -q Running; then
    echo -e "${RED}❌ Grade-service not running. Deploy first: ./scripts/deploy.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Grade-service running${NC}"
echo ""

# Wait for user
read -p "Press Enter to start the demo..."
echo ""

# ==============================================================================
# STEP 1: Check current NetworkPolicy status
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 1: Check Current NetworkPolicy Status${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Current NetworkPolicies in grading-system namespace:"
kubectl get networkpolicies -n grading-system 2>/dev/null || echo "  (none)"
echo ""

read -p "Press Enter to test external egress..."
echo ""

# ==============================================================================
# STEP 2: Test external egress
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 2: Test External Egress${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Get a grade-service pod
GRADE_POD=$(kubectl get pods -n grading-system -l app=grade-service -o jsonpath='{.items[0].metadata.name}')

echo "📤 Testing egress from grade-service to external internet..."
echo "   Pod: $GRADE_POD"
echo "   Target: https://httpbin.org/get"
echo ""
echo "   Result:"
echo "   ─────────────────────────────────────────────────────────────"

# Test external egress
RESULT=$(kubectl exec -n grading-system "$GRADE_POD" -- \
    curl -s --max-time 10 https://httpbin.org/get 2>&1) || RESULT="CONNECTION_FAILED"

if echo "$RESULT" | grep -q "origin"; then
    echo -e "   ${GREEN}✅ EXTERNAL EGRESS ALLOWED!${NC}"
    echo "   Response received from httpbin.org"
    echo ""
    echo -e "   ${YELLOW}NetworkPolicy is allowing external HTTPS traffic.${NC}"
elif echo "$RESULT" | grep -q "CONNECTION_FAILED\|timed out\|Connection refused"; then
    echo -e "   ${RED}❌ EXTERNAL EGRESS BLOCKED!${NC}"
    echo "   Connection failed or timed out"
    echo ""
    echo -e "   ${GREEN}This is expected if you have a default-deny policy!${NC}"
    echo "   NetworkPolicy is blocking HTTPS egress to external services."
else
    echo -e "   ${YELLOW}⚠️  Unexpected response:${NC}"
    echo "   $RESULT"
fi

echo ""
read -p "Press Enter to test internal egress (service-to-service)..."
echo ""

# ==============================================================================
# STEP 3: Test internal egress (service-to-service)
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 3: Test Internal Egress (Service-to-Service)${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "📤 Testing egress from grade-service to student-service..."
echo "   Pod: $GRADE_POD"
echo "   Target: http://student-service:5001/health"
echo ""
echo "   Result:"
echo "   ─────────────────────────────────────────────────────────────"

RESULT=$(kubectl exec -n grading-system "$GRADE_POD" -- \
    curl -s --max-time 5 http://student-service:5001/health 2>&1) || RESULT="CONNECTION_FAILED"

if echo "$RESULT" | grep -q "healthy\|status"; then
    echo -e "   ${GREEN}✅ INTERNAL EGRESS ALLOWED!${NC}"
    echo "   Response: $RESULT"
    echo ""
    echo -e "   ${GREEN}NetworkPolicy allows grade-service → student-service${NC}"
else
    echo -e "   ${RED}❌ INTERNAL EGRESS BLOCKED!${NC}"
    echo "   Response: $RESULT"
    echo ""
    echo -e "   ${YELLOW}Check your NetworkPolicy configuration.${NC}"
fi

echo ""

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}DEMO SUMMARY${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Key Takeaways:"
echo ""
echo "  1. NetworkPolicies control EGRESS (outbound) traffic from pods"
echo ""
echo "  2. By default (with default-deny policy), all egress is blocked"
echo ""
echo "  3. You must explicitly allow:"
echo "     - DNS (port 53) for service discovery"
echo "     - Internal service-to-service communication"
echo "     - External internet access (if needed)"
echo ""
echo "  4. Use cases for egress control:"
echo "     - Preventing data exfiltration"
echo "     - Controlling which services can call external APIs"
echo "     - Compliance and security requirements"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Useful commands:"
echo "  kubectl get networkpolicies -n grading-system"
echo "  kubectl describe networkpolicy <policy-name> -n grading-system"
echo ""
echo "Test egress manually:"
echo "  kubectl exec -it deployment/grade-service -n grading-system -- curl https://httpbin.org/get"
echo ""
