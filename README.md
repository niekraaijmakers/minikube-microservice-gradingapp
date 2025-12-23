# Student Grading System - Microservices on Kubernetes

A microservices-based student grading system designed to teach Kubernetes concepts including **Ingress** (external traffic routing) and **Egress** (network policies controlling outbound traffic).

## 🏗️ Architecture Overview

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                      INTERNET                                │
                    └─────────────────────────────┬───────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                  KUBERNETES CLUSTER                                  │
│  ┌───────────────────────────────────────────────────────────────────────────────┐  │
│  │                              INGRESS CONTROLLER                                │  │
│  │                            (nginx-ingress-controller)                          │  │
│  │                                                                                │  │
│  │    Routes:                                                                     │  │
│  │      /              → frontend-service                                         │  │
│  │      /api/students  → student-service                                          │  │
│  │      /api/grades    → grade-service                                            │  │
│  └───────────────────────────────────────┬───────────────────────────────────────┘  │
│                                          │                                          │
│    ┌─────────────────────────────────────┼─────────────────────────────────────┐    │
│    │                                     ▼                                      │    │
│    │   ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐        │    │
│    │   │   FRONTEND   │    │ STUDENT-SERVICE  │    │  GRADE-SERVICE   │        │    │
│    │   │              │───▶│                  │◀───│                  │        │    │
│    │   │  Port: 5000  │    │   Port: 5001     │    │   Port: 5002     │        │    │
│    │   │              │───▶│                  │    │                  │        │    │
│    │   └──────────────┘    └────────┬─────────┘    └────────┬─────────┘        │    │
│    │          │                     │                       │                   │    │
│    │          │                     ▼                       ▼                   │    │
│    │          │            ┌────────────────────────────────────────┐          │    │
│    │          │            │              DATABASE                   │          │    │
│    │          │            │         (In-memory SQLite)              │          │    │
│    │          │            └────────────────────────────────────────┘          │    │
│    │          │                                                                 │    │
│    │          │     ╔═══════════════════════════════════════════════════╗      │    │
│    │          │     ║              NETWORK POLICIES                      ║      │    │
│    │          │     ║  ─────────────────────────────────────────────────║      │    │
│    │          │     ║  • Default: DENY all ingress/egress               ║      │    │
│    │          │     ║  • Frontend → can reach student & grade services  ║      │    │
│    │          │     ║  • Grade Service → can reach student service      ║      │    │
│    │          │     ║  • Student Service → BLOCKED from external        ║      │    │
│    │          │     ╚═══════════════════════════════════════════════════╝      │    │
│    │                                                                            │    │
│    │                          grading-system namespace                          │    │
│    └────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
minikube-cluster/
├── services/                      # Microservices source code
│   ├── student-service/           # Student management API (port 5001)
│   ├── grade-service/             # Grade management API (port 5002)
│   └── frontend/                  # Web UI (port 5000)
│
├── k8s/                           # Kubernetes manifests
│   ├── namespace.yaml             # grading-system namespace
│   ├── deployments/               # Deployment configs
│   ├── services/                  # Service configs
│   ├── ingress/                   # Ingress routing rules
│   └── network-policies/          # Egress/Ingress restrictions
│
├── scripts/                       # Helper scripts
│   ├── setup-minikube.sh          # Initialize minikube with Calico CNI
│   ├── build-images.sh            # Build Docker images in minikube
│   ├── deploy.sh                  # Deploy all services
│   ├── demo-egress.sh             # Interactive egress demonstration
│   └── cleanup.sh                 # Remove all resources
│
├── docs/                          # Documentation
│   ├── INGRESS_EXPLAINED.md       # Ingress concepts
│   └── EGRESS_EXPLAINED.md        # Egress concepts
│
├── ARCHITECTURE.md                # Detailed architecture docs
└── ASSIGNMENT.md                  # Intern assignment instructions
```

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Minikube installed (`brew install minikube`)
- kubectl installed (`brew install kubectl`)

### 1. Start Minikube with CNI Plugin

```bash
# Start minikube with Calico CNI (required for NetworkPolicies)
./scripts/setup-minikube.sh
```

### 2. Build and Deploy

```bash
# Build Docker images inside minikube
./scripts/build-images.sh

# Deploy all services
./scripts/deploy.sh
```

### 3. Access the Application

```bash
# Get the ingress URL
minikube service frontend -n grading-system --url

# Or use minikube tunnel for LoadBalancer access
minikube tunnel
```

Then visit: `http://grading.local` (after adding to /etc/hosts)

## 🎯 Learning Objectives

### Ingress (Traffic INTO the cluster)
- How external HTTP requests reach internal services
- URL-based routing to different microservices
- TLS termination concepts

### Egress (Traffic OUT from pods)
- NetworkPolicies controlling pod-to-pod communication
- Restricting external internet access from pods
- Service mesh concepts (egress gateways)

## 📚 Key Concepts Demonstrated

| Concept | How It's Demonstrated |
|---------|----------------------|
| **Ingress** | nginx-ingress routes `/api/students`, `/api/grades`, and `/` to different services |
| **Egress NetworkPolicy** | Pods trying to reach external internet - blocked by default! |
| **Ingress NetworkPolicy** | Only ingress controller can reach frontend; only frontend reaches backend |
| **Service Discovery** | Services communicate via Kubernetes DNS (`student-service.grading-system.svc`) |
| **Microservices** | Three independent services with their own APIs |

## 🎯 Egress Demo

Test how NetworkPolicies control outbound traffic:

```bash
# Test external egress from a pod (should be blocked with default-deny policy)
kubectl exec -it deployment/grade-service -n grading-system -- \
    curl -s --max-time 5 https://httpbin.org/get

# Test internal service-to-service communication (should work)
kubectl exec -it deployment/grade-service -n grading-system -- \
    curl -s http://student-service:5001/health
```

Or run the interactive demo:
```bash
./scripts/demo-egress.sh
```

## 🔧 Useful Commands

```bash
# View all resources in the namespace
kubectl get all -n grading-system

# View ingress rules
kubectl describe ingress -n grading-system

# View network policies
kubectl get networkpolicies -n grading-system
kubectl describe networkpolicy -n grading-system

# Check pod logs
kubectl logs -f deployment/frontend -n grading-system
kubectl logs -f deployment/student-service -n grading-system
kubectl logs -f deployment/grade-service -n grading-system

# Test egress restrictions (from inside a pod)
kubectl exec -it deployment/student-service -n grading-system -- curl -s --max-time 5 https://httpbin.org/get
# Should be BLOCKED by NetworkPolicy!

# Test internal communication
kubectl exec -it deployment/grade-service -n grading-system -- curl http://student-service:5001/api/students
# Should WORK (allowed by NetworkPolicy)
```

## 🎓 For Interns

See [ASSIGNMENT.md](./ASSIGNMENT.md) for your assignment instructions. You'll be extending this system with new microservices!

