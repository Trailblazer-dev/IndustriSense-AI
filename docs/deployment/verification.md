# ✅ Verification & Testing Guide

Procedures for validating the IndustriSense AI platform integrity and performance.

---

## ⚡ Quick Verification (Post-Deployment)

### 1. Connectivity Check
Verify that the web engine and database are communicating.
```bash
# From host machine
curl -I http://localhost:5000/
```
**Expected:** `HTTP/1.1 200 OK` (or `302 Found` if redirecting to login).

### 2. Fleet Scaling Verification
Log in as a subscribed user and verify that the dashboard reflects the correct machine count.
- **Production Pro:** Should display **50 machines** (or the specific count set in DB).
- **Industrial Nexus:** Should scale based on organizational data.

---

## 🧪 Comprehensive Testing

### 1. Automated Integration Suite
Run the centralized test suite inside the application container.
```bash
docker exec -it industrisense_app python -m unittest discover tests/
```
**Pass Criteria:**
- `test_ml_service_logic`: Inference engine returns non-zero variance.
- `test_organization_fleet_scaling`: Fleet size matches DB configuration.

### 2. Manual ML Pipeline Audit
Verify that the dual-core engine is correctly processing features.
```python
# Inside python console
from app.services import ml_service as mls
data = mls.get_data()
# Verify Raw vs Scaled separation
print(data['raw']['Tool wear [min]'].iloc[0])    # Expected: Integer (e.g. 50)
print(data['scaled']['Tool wear [min]'].iloc[0]) # Expected: Float (e.g. -0.42)
```

---

## 📋 Pre-Production Checklist

### Data Integrity
- [ ] `features_engineered_raw.csv` and `features_engineered_scaled.csv` present in `data/processed/`.
- [ ] Model artifacts (`.pkl` and `.xgb`) verified in `src/models/`.

### Security
- [ ] `SECRET_KEY` set via environment variable.
- [ ] CSRF tokens active on all interactive forms (Login, Register, Checkout, Archive).
- [ ] Multi-tenant isolation verified (User A cannot view User B's fleet).

### Infrastructure
- [ ] Celery worker is active and registered to the `background_fleet_analysis` task.
- [ ] Redis broker connection is healthy.
- [ ] Gunicorn timeout set to **120s** to handle high-recall inference loads.

---

## 📊 Performance Baselines

| Component | Target Metric |
|-----------|---------------|
| **Dashboard Load** | < 500ms (for 50 machines) |
| **Diagnostic API** | < 300ms |
| **Payment STK Push** | < 5s trigger time |
| **Worker Inference** | < 2s for full fleet re-score |

---

**Last Updated:** March 2026  
**Status:** Validated & Hardened
