# 🌐 IndustriSense AI - Web Application

Enterprise-grade predictive maintenance dashboard. This application serves as the user interface for the IndustriSense AI inference engine, providing real-time fleet health monitoring and automated work order generation.

## ✨ Core Features

### 🎨 Industrial Dashboard
- **Sleek Sidebar Navigation:** Fast access to Operations, Analytics, and Config.
- **Premium "Nexus" KPI Ribbon:** High-level fleet metrics (Utilization, Health Index, Protected Assets).
- **Interactive Asset Grid:** Dynamic machine tiles with live risk gauges and sorted prioritization.
- **Diagnostic Modals:** Deep-dive reports with AI-justified maintenance recommendations.

### 💳 Tiered Industrial Licensing
- **Operational Base:** Basic monitoring for up to 10 machines.
- **Production Pro:** Advanced RUL forecasting and automated audit reports.
- **Industrial Nexus:** Enterprise-wide CMMS integration and unlimited fleet scaling.
- **M-Pesa Integration:** Secure STK Push payments via PayHero Kenya.

### 🧠 Analytical Intelligence
- **Dual XGBoost Engine:** Parallel processing of failure risk and component wear.
- **Permutation XAI:** Human-readable explanations for every model decision.
- **Fleet-Wide Vectorization:** Optimized inference paths for massive industrial datasets.

---

## 🏗️ Technical Stack

- **Backend:** Flask 3.0.0 (Python 3.10+)
- **Frontend:** Bootstrap 5, FontAwesome 6, Vanilla JS
- **Database:** PostgreSQL 15 (SQLAlchemy ORM)
- **Task Queue:** Celery 5.3 + Redis 7.0
- **Security:** Talisman (CSP), CSRF Protection, Rate Limiting

---

## 🚀 Quick Start (Local Docker)

The easiest way to run the web application is via Docker Compose from the project root:

```bash
docker compose up --build -d
```

Access the dashboard at: [http://localhost:5000](http://localhost:5000)

---

## 🔌 Internal API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Global health statistics. |
| `/api/machine/<id>` | GET | Full diagnostic report for a specific asset. |
| `/api/predict` | POST | Ad-hoc telemetry analysis. |

---

## 🔧 Configuration

All critical settings are managed via environment variables in `docker-compose.yml`:
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: Celery message broker.
- `SECRET_KEY`: Flask session security.
- `PAYHERO_CHANNEL_ID`: M-Pesa gateway configuration.

---

**Last Updated:** March 2026  
**Status:** Operational
