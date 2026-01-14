# Makefile for Minikube Grading System
# =====================================

.PHONY: all setup build deploy clean restart logs port-forward help

# Default target
all: setup build deploy

# Full setup: create cluster, build images, deploy
setup:
	@echo "🚀 Setting up Minikube cluster..."
	./scripts/setup-minikube.sh

# Build all Docker images
build:
	@echo "📦 Building Docker images..."
	./scripts/build-images.sh

# Deploy to Kubernetes
deploy: build 
	@echo "🎯 Deploying to Kubernetes..."
	./scripts/deploy.sh

# Full rebuild: setup + build + deploy
full: setup build deploy

# Clean up: delete minikube cluster
clean:
	@echo "🧹 Cleaning up..."
	./scripts/cleanup.sh

# Restart all deployments
restart:
	@echo "🔄 Restarting all deployments..."
	kubectl rollout restart deployment -n grading-system

# Rebuild and restart (no cluster recreation)
rebuild: build restart
	@echo "✅ Rebuild complete"

# Show logs for all services
logs:
	@echo "📋 Showing logs..."
	kubectl logs -n grading-system -l app=frontend --tail=20 & \
	kubectl logs -n grading-system -l app=grade-service --tail=20 & \
	kubectl logs -n grading-system -l app=notification-service --tail=20 & \
	kubectl logs -n grading-system -l app=student-service --tail=20

# Logs for specific services
logs-frontend:
	kubectl logs -n grading-system -l app=frontend -f

logs-grade:
	kubectl logs -n grading-system -l app=grade-service -f

logs-notification:
	kubectl logs -n grading-system -l app=notification-service -f

logs-student:
	kubectl logs -n grading-system -l app=student-service -f

# Port forward to frontend
port-forward:
	@echo "🌐 Port forwarding to frontend on http://localhost:5000"
	kubectl port-forward -n grading-system svc/frontend 5000:5000

# Show pod status
status:
	@echo "📊 Pod status:"
	kubectl get pods -n grading-system
	@echo ""
	@echo "🔒 Network policies:"
	kubectl get networkpolicies -n grading-system

# Apply network policies only
policies:
	@echo "🔒 Applying network policies..."
	kubectl apply -f k8s/network-policies/

# Help
help:
	@echo "Available targets:"
	@echo "  make all          - Setup cluster, build images, deploy (default)"
	@echo "  make setup        - Setup Minikube cluster only"
	@echo "  make build        - Build Docker images only"
	@echo "  make deploy       - Deploy to Kubernetes only"
	@echo "  make full         - Full setup (same as 'all')"
	@echo "  make rebuild      - Rebuild images and restart pods"
	@echo "  make restart      - Restart all deployments"
	@echo "  make clean        - Delete Minikube cluster"
	@echo "  make logs         - Show recent logs from all services"
	@echo "  make logs-frontend    - Follow frontend logs"
	@echo "  make logs-grade       - Follow grade-service logs"
	@echo "  make logs-notification - Follow notification-service logs"
	@echo "  make logs-student     - Follow student-service logs"
	@echo "  make port-forward - Port forward frontend to localhost:5000"
	@echo "  make status       - Show pod and network policy status"
	@echo "  make policies     - Apply network policies only"
	@echo "  make help         - Show this help"

