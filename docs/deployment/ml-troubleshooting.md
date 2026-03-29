# 🔧 ML Troubleshooting & Debugging

Diagnostic guide for resolving common machine learning pipeline issues.

---

## ⚡ Symptom: Constant Predictions
**All machines show the same risk or wear (e.g., 5.3 min regardless of input)**

### Root Cause: Scale Mismatch
The XGBoost regressor is trained on **RAW** data but receives **SCALED** data at inference.
- **Fix:** Ensure `get_data()` in `ml_service.py` correctly handles both `features_engineered_raw.csv` and `features_engineered_scaled.csv`.
- **Logic:** Classifier MUST use Scaled features; Regressor MUST use Raw features.

---

## ⚡ Symptom: HTTP 403 Access Denied
**Operators see "Access Denied" when clicking machine tiles.**

### Root Cause: Multi-Tenancy Mismatch
The API strictly verifies that the requested `machine_id` belongs to the user's organization based on their `machine_count`.
- **Fix:** Ensure the organization's `machine_count` in the database matches the number of assets being monitored.
- **DB Command:** `UPDATE organizations SET machine_count = 50 WHERE id = <ID>;`

---

## ⚡ Symptom: "Unexpected token <" in Dashboard
**Diagnostic modals show a JSON parsing error.**

### Root Cause: Redirect to Login/Plans
A fetch request to `/api/machine/<id>` is being redirected to an HTML page (usually Login or Plans) because of insufficient permissions or an expired session.
- **Fix:** Ensure the user has the required **Operational Base** plan or higher. 
- **Check:** Verify that `is_archive=False` is passed correctly in the reports route.

---

## 🧪 Model Verification Commands

### Check Artifact Integrity
```bash
# Verify model files exist and match checksums
ls -l src/models/*.pkl
sha256sum src/models/xgboost_wear_regressor.xgb
```

### Force Model Reload
If models are updated in the repository but not in the container:
```bash
docker compose restart web worker
```

---

## 📊 Expected Performance Baseline

| Metric | Target | Interpretation |
|--------|--------|----------------|
| **Recall** | > 95% | Zero missed catastrophic failures. |
| **Precision** | > 80% | Minimize "false alarm" maintenance calls. |
| **RUL MAE** | < 2 min | Accurate maintenance scheduling. |

---

**Last Updated:** March 2026  
**Version:** 3.5
