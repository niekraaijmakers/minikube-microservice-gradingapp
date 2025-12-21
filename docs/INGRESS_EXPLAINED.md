# Understanding Kubernetes Ingress

## What is Ingress?

**Ingress** is a Kubernetes resource that manages external access to services within a cluster, typically HTTP/HTTPS traffic. It provides:
- **Load balancing**
- **SSL/TLS termination**
- **Name-based virtual hosting**
- **Path-based routing**

## Without Ingress

Without Ingress, you would need to expose each service individually:

```
Internet → LoadBalancer Service → Pod (Service A)
Internet → LoadBalancer Service → Pod (Service B)
Internet → LoadBalancer Service → Pod (Service C)
```

This requires multiple external IPs/load balancers, which is expensive.

## With Ingress

Ingress provides a single entry point:

```
                    ┌─────────────────────────────┐
Internet ─────────▶ │    Ingress Controller       │
                    │    (nginx, traefik, etc.)    │
                    └─────────────┬───────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   /api/users              /api/products                   /
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ User Service  │    │Product Service│    │   Frontend    │
└───────────────┘    └───────────────┘    └───────────────┘
```

## Key Components

### 1. Ingress Resource
A Kubernetes object that defines routing rules:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 80
```

### 2. Ingress Controller
The actual component that implements the Ingress rules. Common controllers:
- **nginx-ingress** (most popular)
- **Traefik**
- **HAProxy**
- **AWS ALB Ingress Controller**

The controller watches for Ingress resources and configures its underlying proxy.

## Path Types

| PathType | Description |
|----------|-------------|
| `Exact` | Matches the URL path exactly |
| `Prefix` | Matches based on URL path prefix |
| `ImplementationSpecific` | Depends on the IngressClass |

## In This Project

Our Ingress configuration routes:

```
http://grading.local/              → frontend:5000
http://grading.local/api/students  → student-service:5001
http://grading.local/api/grades    → grade-service:5002
```

## Useful Commands

```bash
# View ingress resources
kubectl get ingress -n grading-system

# Describe ingress (see routing rules)
kubectl describe ingress grading-ingress -n grading-system

# View ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Test ingress
curl -H "Host: grading.local" http://$(minikube ip)/api/students
```

## Common Issues

1. **503 Service Unavailable**: Service or pods not ready
2. **404 Not Found**: Path doesn't match any rule
3. **Connection refused**: Ingress controller not running
4. **No address assigned**: Waiting for external IP (use `minikube tunnel`)

