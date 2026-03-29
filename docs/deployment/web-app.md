# 🌐 Web Application Documentation

IndustriSense AI is an enterprise SaaS platform built on the Flask ecosystem, optimized for high-performance industrial monitoring and secure multi-tenancy.

---

## 🏛️ Application Architecture

The platform follows a modular **Blueprint**-based architecture to ensure scalability and maintainability.

### Core Stack
- **Framework:** Flask 3.0.0+ (Python 3.10+)
- **Database:** PostgreSQL 15 (Production) / SQLite (Local/Testing)
- **Task Queue:** Celery 5.3+ with Redis 7.0+
- **Security:** Flask-WTF (CSRF), Flask-Limiter, Flask-Talisman (CSP/HSTS)
- **ML Engine:** Dual XGBoost Inference Cores
- **UI:** Bootstrap 5 with "Industrial Dark" professional theme

---

## 🛡️ Access Control & Multi-Tenancy

### Domain-Based Isolation
Organizations are automatically created based on user email domains (e.g., `@factory.com`). All data queries are scoped by `organization_id` to prevent cross-tenant leakage.

### Subscription Tiers
| Tier | Access Level | Key Features |
|------|--------------|--------------|
| **Operational Base** | Entry | Fleet Dashboard, Failure Risk, Basic XAI. |
| **Production Pro** | Advanced | RUL Forecasting, Maintenance Reporting, Archiving. |
| **Industrial Nexus** | Enterprise | Unlimited Fleet, CMMS Sync, Financial Audits. |

---

## 🚀 Deployment

### Docker Orchestration (Production)
The system is fully containerized. Use the provided `docker-compose.yml` for rapid deployment.

```bash
docker compose up --build -d
```

**Services:**
- `db`: Persistent PostgreSQL storage.
- `redis`: Message broker for Celery tasks.
- `web`: Gunicorn-powered Flask API.
- `worker`: Celery process for fleet-wide background inference.

### Render Configuration
The platform is optimized for **Render** via `render.yaml`.
- **Environment:** Managed Postgres and Redis instances.
- **Commands:** Automatically uses the Dockerfile for both web and worker services.

---

## 🔌 API Reference (Internal)

| Endpoint | Method | Plan Required | Description |
|----------|--------|---------------|-------------|
| `/api/stats` | GET | Operational Base | Aggregate health metrics for the fleet. |
| `/api/machine/<id>` | GET | Operational Base | Detailed telemetry and XAI report. |
| `/api/predict` | POST | Production Pro | Manual inference using sensor snapshots. |

---

## 📊 Infrastructure Performance

- **Inference Latency:** < 300ms for single-machine diagnostics.
- **Worker Concurrency:** Optimized for 4 prefork workers per container.
- **Connection Robustness:** Implements SQLAlchemy `pool_pre_ping` and 20s timeouts to handle heavy industrial loads.

---

**Last Updated:** March 2026  
**Status:** Enterprise Hardened
