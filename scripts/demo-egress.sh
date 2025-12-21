#!/bin/bash
# ==============================================================================
# Egress Network Policy Demonstration
# ==============================================================================
# This script demonstrates how NetworkPolicies control EGRESS (outbound) traffic.
#
# The demo uses the webhook notification feature:
# - Grade-service tries to send a webhook to webhook-receiver when a grade is created
# - By default, this is BLOCKED by NetworkPolicy
# - After applying the allow policy, it SUCCEEDS
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
echo "Scenario:"
echo "  • Grade-service wants to send webhook notifications to an external service"
echo "  • The webhook-receiver runs in a different namespace (simulating external)"
echo "  • NetworkPolicy controls whether this communication is allowed"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Check if services are running
echo "🔍 Checking services..."
if ! kubectl get pods -n grading-system -l app=grade-service 2>/dev/null | grep -q Running; then
    echo -e "${RED}❌ Grade-service not running. Deploy first: ./scripts/deploy.sh${NC}"
    exit 1
fi

if ! kubectl get pods -n external-services -l app=webhook-receiver 2>/dev/null | grep -q Running; then
    echo -e "${RED}❌ Webhook-receiver not running. Deploy first: ./scripts/deploy.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All services running${NC}"
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

# Check if webhook egress policy exists
if kubectl get networkpolicy allow-webhook-egress -n grading-system 2>/dev/null; then
    echo -e "${YELLOW}⚠️  The allow-webhook-egress policy is already applied.${NC}"
    echo "   Webhooks will SUCCEED. Delete it to see the blocked behavior:"
    echo "   kubectl delete networkpolicy allow-webhook-egress -n grading-system"
    WEBHOOK_ALLOWED=true
else
    echo -e "${GREEN}✅ Webhook egress policy NOT applied - webhooks will be BLOCKED${NC}"
    WEBHOOK_ALLOWED=false
fi
echo ""

read -p "Press Enter to test the webhook..."
echo ""

# ==============================================================================
# STEP 2: Test webhook (should fail if policy not applied)
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 2: Test Webhook Notification${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "📤 Sending test webhook from grade-service to webhook-receiver..."
echo "   (grade-service namespace: grading-system)"
echo "   (webhook-receiver namespace: external-services)"
echo ""

# Get a grade-service pod
GRADE_POD=$(kubectl get pods -n grading-system -l app=grade-service -o jsonpath='{.items[0].metadata.name}')

echo "   Using pod: $GRADE_POD"
echo "   Command: curl -X POST http://webhook-receiver.external-services:5005/webhook/grade-notification"
echo ""
echo "   Result:"
echo "   ─────────────────────────────────────────────────────────────"

# Test the webhook
RESULT=$(kubectl exec -n grading-system "$GRADE_POD" -- \
    curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"event":"test","message":"Egress demo test"}' \
    --max-time 5 \
    http://webhook-receiver.external-services.svc.cluster.local:5005/webhook/grade-notification 2>&1) || RESULT="CONNECTION_FAILED"

if echo "$RESULT" | grep -q "success"; then
    echo -e "   ${GREEN}✅ WEBHOOK SUCCEEDED!${NC}"
    echo "   $RESULT"
    echo ""
    echo -e "   ${YELLOW}The webhook egress policy is allowing traffic.${NC}"
else
    echo -e "   ${RED}❌ WEBHOOK BLOCKED!${NC}"
    echo "   Connection failed or timed out"
    echo ""
    echo -e "   ${GREEN}This is expected! NetworkPolicy is blocking egress to external-services.${NC}"
fi

echo ""
read -p "Press Enter to continue..."
echo ""

# ==============================================================================
# STEP 3: Show how to allow webhook egress
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 3: Enable Webhook Egress${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

if [ "$WEBHOOK_ALLOWED" = false ]; then
    echo "To ALLOW webhooks, apply the egress policy:"
    echo ""
    echo -e "   ${YELLOW}kubectl apply -f $K8S_DIR/network-policies/06-allow-webhook-egress.yaml${NC}"
    echo ""
    
    read -p "Apply the policy now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔓 Applying allow-webhook-egress policy..."
        kubectl apply -f "$K8S_DIR/network-policies/06-allow-webhook-egress.yaml"
        echo ""
        echo -e "${GREEN}✅ Policy applied! Webhooks should now work.${NC}"
        echo ""
        
        sleep 2
        
        echo "📤 Testing webhook again..."
        echo ""
        
        RESULT=$(kubectl exec -n grading-system "$GRADE_POD" -- \
            curl -s -X POST \
            -H "Content-Type: application/json" \
            -d '{"event":"test","message":"Egress demo test after policy"}' \
            --max-time 5 \
            http://webhook-receiver.external-services.svc.cluster.local:5005/webhook/grade-notification 2>&1) || RESULT="CONNECTION_FAILED"
        
        if echo "$RESULT" | grep -q "success"; then
            echo -e "   ${GREEN}✅ WEBHOOK NOW SUCCEEDS!${NC}"
            echo "   $RESULT"
        else
            echo -e "   ${RED}Still failing - may need a moment to propagate${NC}"
        fi
    fi
else
    echo "Webhook policy is already applied."
    echo ""
    echo "To see the BLOCKED behavior, delete the policy:"
    echo -e "   ${YELLOW}kubectl delete networkpolicy allow-webhook-egress -n grading-system${NC}"
fi

echo ""
echo ""

# ==============================================================================
# STEP 4: View webhook logs
# ==============================================================================
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BLUE}STEP 4: View Webhook Receiver Logs${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

echo "📋 Recent webhook-receiver logs:"
echo "   ─────────────────────────────────────────────────────────────"
kubectl logs -n external-services -l app=webhook-receiver --tail=10 2>/dev/null || echo "   (no logs)"
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
echo "  3. To allow specific egress, you must create a NetworkPolicy that:"
echo "     - Selects the SOURCE pod (podSelector)"
echo "     - Specifies the DESTINATION (namespaceSelector + podSelector)"
echo "     - Specifies the PORTS"
echo ""
echo "  4. This is useful for:"
echo "     - Preventing data exfiltration"
echo "     - Controlling which services can call external APIs"
echo "     - Enforcing microservice communication patterns"
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Useful commands:"
echo "  kubectl get networkpolicies -n grading-system"
echo "  kubectl describe networkpolicy allow-webhook-egress -n grading-system"
echo "  kubectl logs -f -n external-services -l app=webhook-receiver"
echo ""
