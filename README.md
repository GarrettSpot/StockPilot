# StockPilot — Inventory Management (DevOps Capstone)

StockPilot is a small SaaS-style inventory management application used as the
subject of the Session 21 DevOps capstone. It tracks products, stock levels and
reorder thresholds, and is shipped through a full CI/CD and observability stack.

> This is an original application domain (inventory management), not a copy of
> the reference TaskBoard app. The DevOps architecture follows the course model.

## Video Presentation

https://github.com/user-attachments/assets/21303fd8-bb0a-4dd7-9471-f39fc655877d

## Stack

- **Frontend:** React + Vite, responsive dashboard, served by Nginx (non-root)
- **Backend:** FastAPI + SQLAlchemy + Alembic, Prometheus metrics
- **Database:** PostgreSQL 16
- **CI/CD:** GitHub Actions → build, Trivy scan, push to GHCR, Helm deploy
- **Infra:** Terraform (AWS VPC + EKS), Helm, Ingress, HPA
- **Observability:** Prometheus + Grafana (`/metrics`, ServiceMonitor)

## Architecture

```text
Browser ──► Ingress ──► frontend (React/Nginx)
                    └─► backend (FastAPI) ──► PostgreSQL
                                   ▲
                             Prometheus ──► Grafana
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Liveness probe |
| GET | `/ready` | Readiness probe (checks DB) |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/products` | List products |
| GET | `/api/products/{id}` | Get one product |
| POST | `/api/products` | Create product |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| GET | `/api/products/stats` | Aggregate stock stats |

Swagger UI: `/docs`.

## Run locally (Docker Compose)

```bash
docker compose up --build
# App:     http://localhost:3000
# API:     http://localhost:8000/docs
docker compose down -v
```

## Run backend directly

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://stockpilot:stockpilot@localhost:5432/stockpilot'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

## Tests

```bash
cd backend
pytest -v
```

## Kubernetes / Helm

```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install stockpilot ./helm/stockpilot \
  -n stockpilot --create-namespace \
  -f helm/stockpilot/values-dev.yaml
kubectl get pods,svc,hpa -n stockpilot
```

## Terraform (AWS VPC + EKS)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init && terraform plan && terraform apply
aws eks update-kubeconfig --region ap-south-1 --name stockpilot-eks
# ... demo ...
terraform destroy
```

## Monitoring

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml
```

## Repository layout

```text
stockpilot/
├── frontend/            React + Vite app, Dockerfile (multi-stage, non-root)
├── backend/             FastAPI app, tests, Alembic migrations, Dockerfile
├── helm/stockpilot/     Helm chart (deployments, services, ingress, HPA, ServiceMonitor)
├── k8s/                 namespace manifest
├── terraform/           AWS VPC + EKS
├── monitoring/          Prometheus/Grafana values
├── troubleshooting/     deliberately broken manifests for the lab
├── scripts/             load-test helper for HPA demos
└── .github/workflows/   CI/CD pipeline
```
