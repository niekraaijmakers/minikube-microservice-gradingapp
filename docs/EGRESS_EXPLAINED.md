# Understanding Kubernetes Egress & Network Policies

## What is Egress?

**Egress** refers to outbound traffic FROM pods TO other destinations. This includes:
- Pod-to-pod communication
- Pod-to-service communication
- Pod-to-external-internet communication

## The Problem: Default Behavior

By default, Kubernetes allows **all** network traffic:
- Any pod can talk to any other pod
- Any pod can talk to the internet
- Any pod can talk to any service

This is convenient but **insecure**. In production, you want:
- Database pods only accessible by application pods
- Sensitive services isolated from others
- External internet access restricted

## The Solution: Network Policies

**NetworkPolicies** are Kubernetes resources that control traffic flow at the IP/port level.

### How They Work

1. **Without NetworkPolicy**: All traffic allowed
2. **With NetworkPolicy**: Only explicitly allowed traffic works

Think of it like a firewall:
```
Default: ALLOW ALL

With NetworkPolicy: DENY ALL, except...
  - Allow frontend → backend
  - Allow backend → database
  - Block backend → internet
```

## Types of Rules

### Ingress Rules (Traffic INTO a pod)
```yaml
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: frontend
    ports:
    - port: 8080
```
This allows only pods with `role: frontend` to reach `my-app` on port 8080.

### Egress Rules (Traffic OUT of a pod)
```yaml
spec:
  podSelector:
    matchLabels:
      app: my-app
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - port: 5432
```
This allows `my-app` to only connect to the database on port 5432.

## Network Policy in This Project

### Policy Structure

```
┌──────────────────────────────────────────────────────────────────┐
│                         grading-system                           │
│                                                                  │
│   ┌────────────┐                                                 │
│   │  FRONTEND  │──────────────────────┐                         │
│   │            │──────────────────┐   │                         │
│   └────────────┘                  │   │                         │
│         ▲                         ▼   ▼                         │
│         │                    ┌──────────┐    ┌──────────┐       │
│   From Ingress               │ STUDENT  │◀───│  GRADE   │       │
│   Controller                 │ SERVICE  │    │ SERVICE  │       │
│                              └──────────┘    └────┬─────┘       │
│                                                   │              │
│                                                   ▼              │
│                                            ┌──────────────┐     │
│                                            │   EXTERNAL   │     │
│                                            │   INTERNET   │     │
│                                            │      ❌       │     │
│                                            │   BLOCKED    │     │
│                                            └──────────────┘     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Policies Applied

| Policy | Purpose |
|--------|---------|
| `default-deny-all` | Block all traffic by default |
| `allow-dns` | Allow DNS resolution (required) |
| `allow-ingress-to-frontend` | Ingress controller → Frontend |
| `allow-ingress-to-apis` | Ingress controller → APIs |
| `allow-frontend-egress` | Frontend → Backend services |
| `allow-grade-to-student` | Grade service → Student service |

### What's Allowed vs Blocked

| Source | Destination | Allowed? |
|--------|-------------|----------|
| Frontend | Student Service | ✅ Yes |
| Frontend | Grade Service | ✅ Yes |
| Grade Service | Student Service | ✅ Yes |
| Grade Service | google.com | ❌ No |
| Student Service | Grade Service | ❌ No |
| Student Service | Internet | ❌ No |

## Testing Network Policies

### Test Allowed Traffic
```bash
# From grade-service, call student-service (should work)
kubectl exec -it deployment/grade-service -n grading-system -- \
    curl -s http://student-service:5001/health
```

### Test Blocked Traffic
```bash
# From grade-service, try to reach internet (should fail)
kubectl exec -it deployment/grade-service -n grading-system -- \
    curl -s --max-time 5 http://google.com
# This should timeout!
```

## CNI Requirement

Network Policies require a **CNI plugin** that supports them:
- ✅ Calico
- ✅ Cilium
- ✅ Weave Net
- ❌ Flannel (basic version)

In this project, we use **Calico** (enabled with `minikube start --cni=calico`).

## Useful Commands

```bash
# List network policies
kubectl get networkpolicies -n grading-system

# Describe a policy
kubectl describe networkpolicy allow-grade-to-student -n grading-system

# Delete policies to test without them
kubectl delete networkpolicies --all -n grading-system

# Re-apply policies
kubectl apply -f k8s/network-policies/
```

## Common Gotchas

1. **DNS not working**: You MUST allow egress to kube-dns
2. **Policies are additive**: Multiple policies combine their rules
3. **Empty selector = all pods**: `podSelector: {}` matches everything
4. **No rules = deny all**: An empty ingress/egress list blocks everything

