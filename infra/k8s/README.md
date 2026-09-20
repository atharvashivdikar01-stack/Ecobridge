# infra/k8s ☸️

Production Kubernetes manifests and Helm charts for deploying ECOBRIDGE services.

## Architecture
- **API Server:** Horizontal Pod Autoscaler (HPA) targeting 70% CPU/Memory utilization.
- **Web Applications:** Node SSR pods fronted by NGINX Ingress Controller with TLS termination.
- **Workers:** BullMQ consumers for background sync processing and market price scrapers.
