# 🔴 RUL Regressor Retraining Guide

## Problem: Data Leakage in Current Model

The current XGBoost RUL regressor was trained with **leaky features**:
- `Stress Index = Torque × Tool Wear` ← **Uses the target variable**
- `Temp_Diff_x_Wear = Temp Diff × Tool Wear` ← **Uses the target variable**

**Impact:**
- Fake R² = 0.9995 (unrealistically perfect)
- Model is not production-ready
- RUL predictions are unreliable

---

## Solution: Fix Feature Engineering in Notebook 4

### Step 1: Open Notebook 4
```
notebooks/4_RUL_Prognosis_Modeling.ipynb
```

### Step 2: Fix the Feature List (Cell ~7 - Data Preparation)

**BEFORE (Current - LEAKY):**
```python
feature_cols = ['Air temperature [K]', 'Process temperature [K]', 
                'Rotational speed [rpm]', 'Torque [Nm]',
                'Stress Index', 'Temp Diff [K]',    # ← REMOVE: Stress Index
                'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly']  # ← REMOVE: Temp_Diff_x_Wear
```

**AFTER (CLEAN - NO LEAKAGE):**
```python
feature_cols = ['Air temperature [K]', 'Process temperature [K]', 
                'Rotational speed [rpm]', 'Torque [Nm]',
                'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly']
```

### Step 3: Run the Entire Notebook

Execute all cells from top to bottom. This will:
1. Load data with clean features (7 features instead of 9)
2. Perform 80/20 train/test split
3. Train new XGBoost regressor without leaky features
4. Save new model to `src/models/xgboost_wear_regressor.pkl`
5. Update metadata in `src/models/rul_metadata.json`

### Step 4: Verify the Results

Check the diagnostics endpoint after retraining:
```
GET /diagnostics/model-calibration
```

Expected changes:
- R² will drop from 0.9995 to realistic ~0.80-0.90 range
- MAE will be ~3-5 minutes (instead of ~0.88 min)
- Metadata will show 7 features instead of 9

---

## Expected Performance After Retraining

With **clean features** (no leakage):

| Metric | Before (Leaky) | After (Clean) |
|--------|---|---|
| **CV R²** | 0.9996 | ~0.85-0.90 |
| **Test R²** | 0.9996 | ~0.85-0.90 |
| **Test MAE** | 0.88 min | ~3-5 min |
| **Test RMSE** | 1.37 min | ~7-10 min |
| **Production Use** | ❌ NO | ✅ YES |

---

## What Changes in the Web App

Once the model is retrained:

### Option A: Update Feature Columns (Recommended)
Update `FEATURE_COLS_REGRESSOR` in `web_app/app.py`:

```python
FEATURE_COLS_REGRESSOR = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly'
]
```

Remove the leakage warning comments.

### Option B: Keep Backward Compatibility
If you need to keep old benchmarks, add a feature mapping layer that handles both versions.

---

## Timeline

**Immediate Actions:**
- ✅ Web app is now working (using all 9 features from current model)
- ✅ Failure classifier is production-ready (no changes needed)

**Before Production Deployment:**
- [ ] Rerun Notebook 4 with clean features
- [ ] Validate new model performance
- [ ] Update web app feature columns
- [ ] Test dashboard and API endpoints

---

## Questions?

The data leakage issue is **identified and documented**. The model is currently **usable for demonstration** but should be retrained before production use with real data and real operational costs.
