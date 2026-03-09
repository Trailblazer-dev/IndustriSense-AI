# ✅ Verification & Testing Guide

Complete procedures for verifying the ML pipeline is working correctly.

---

## Quick Verification (3 minutes)

### For: Checking if recent fixes are working

**Step 1: Run Verification Script (30 sec)**

```bash
cd web_app
python verify_fix.py
```

**Expected output:**
```
✓ SUCCESS: Fix is working correctly!
Predictions vary across machines
Range: 5.1 - 240.3 minutes
Standard Deviation: 78.4 min
```

**If you see this:** ✅ You're good to go!

---

### Step 2: Restart Flask (30 sec)

```bash
pkill -f "python.*app.py"
python web_app/app.py
```

**Expected:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

---

### Step 3: Visual Check (1 min)

Visit: `http://localhost:5000`

**Check the dashboard:**
- [ ] 10 machines displayed
- [ ] Predicted wear values **VARY** (NOT all 5.3 min)
- [ ] RUL values **VARY** (NOT all 248 min)
- [ ] Failure risk percentages **VARY** (0-100%)

**Example good data:**
```
Machine 1: Wear 5.1 min, RUL 248 min
Machine 2: Wear 145.2 min, RUL 108 min  ← Different!
Machine 3: Wear 89.3 min, RUL 164 min   ← Different!
Machine 4: Wear 210.4 min, RUL 43 min   ← Different!
```

---

## Comprehensive Validation (10 minutes)

### For: Complete system health check

**Prerequisites:**
- Flask app is running
- Models loaded successfully
- Data files accessible

---

### Test 1: Dashboard Displays Correctly

**What to check:**
1. **Page loads** without JavaScript errors
   - Open DevTools (F12)
   - Check Console tab for errors
   - Should be empty or only warnings

2. **All 10 machines visible**
   - Scroll through dashboard
   - Each machine has an ID and status

3. **Failure risk color-coded**
   - 🔴 Red cards: >70% failure probability
   - 🟡 Yellow cards: 30-70% failure probability
   - 🟢 Green cards: <30% failure probability

**Pass Criteria:** All 3 items visible and correct

---

### Test 2: Prediction Variation

**What to check:**
1. **Are predictions unique?**
   ```python
   # Open Python console and verify
   from web_app.app import load_data
   df = load_data()
   
   # Check if "Tool wear [min]" values are different
   wear_values = df['Tool wear [min]'].head(10).tolist()
   print(wear_values)  # Should show different values, not [5.3, 5.3, 5.3, ...]
   ```

2. **Do values fall in expected range?**
   - Wear: [0, 253] minutes
   - RUL: [0, 253] minutes
   - Failure risk: [0%, 100%]

3. **Are error metrics reasonable?**
   - Expected MAE: <2 minutes (matching training accuracy)
   - Expected RMSE: <2 minutes

**Pass Criteria:** ✓ Values vary ✓ In expected ranges ✓ Errors <2 min

---

### Test 3: API Endpoints

**Test `/api/stats`:**
```bash
curl http://localhost:5000/api/stats
```

**Expected response:**
```json
{
  "total_machines": 10,
  "critical_count": 2,
  "warning_count": 4,
  "normal_count": 4,
  "timestamp": "2024-02-22 14:30:00"
}
```

**Test `/api/machines/0`:**
```bash
curl http://localhost:5000/api/machines/0
```

**Expected response:**
```json
{
  "id": 0,
  "failure_probability": 0.423,
  "actual_tool_wear": 87.3,
  "predicted_tool_wear": 85.1,
  "wear_error": 2.2,
  "actual_rul": 165,
  "predicted_rul": 168,
  "status": "WARNING"
}
```

**Test `/api/predict` (POST):**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "air_temp": 300.5,
    "process_temp": 310.2,
    "rpm": 1500,
    "torque": 42.5
  }'
```

**Pass Criteria:** All endpoints respond with valid JSON

---

### Test 4: Data File Validation

**Check data files exist:**
```bash
ls -la data/processed/
```

**Expected files:**
- `features_engineered_raw.csv` (10,000 rows × 16 cols)
- `features_engineered_scaled.csv` (10,000 rows × 16 cols)

**Verify data integrity:**
```python
import pandas as pd

# Load raw data
df_raw = pd.read_csv('data/processed/features_engineered_raw.csv')
print(f"Raw data shape: {df_raw.shape}")  # Should be (10000, 16)
print(f"Wear range: {df_raw['Tool wear [min]'].min()}-{df_raw['Tool wear [min]'].max()}")
# Should be: 0.0-253.0

# Load scaled data
df_scaled = pd.read_csv('data/processed/features_engineered_scaled.csv')
print(f"Scaled data shape: {df_scaled.shape}")  # Should be (10000, 16)
print(f"Wear range: {df_scaled['Tool wear [min]'].min()}-{df_scaled['Tool wear [min]'].max()}")
# Should be approximately: -1.68 to +1.60
```

**Pass Criteria:** Raw range [0-253], Scaled range [-1.68 to +1.60]

---

### Test 5: Model File Validation

**Check model files:**
```bash
ls -la src/models/*.pkl
```

**Expected files:**
- `xgboost_classifier.pkl` (>500 KB)
- `xgboost_wear_regressor.pkl` (>500 KB)

**Verify models load:**
```python
import pickle

# Load classifier
with open('src/models/xgboost_classifier.pkl', 'rb') as f:
    clf = pickle.load(f)
print(f"Classifier loaded: {type(clf).__name__}")

# Load regressor
with open('src/models/xgboost_wear_regressor.pkl', 'rb') as f:
    reg = pickle.load(f)
print(f"Regressor loaded: {type(reg).__name__}")

# Verify they have predict methods
assert hasattr(clf, 'predict_proba'), "Classifier missing predict_proba"
assert hasattr(reg, 'predict'), "Regressor missing predict"
```

**Pass Criteria:** Both models load and have correct methods

---

### Test 6: Feature Engineering Verification

**Check feature columns match:**
```python
from web_app.app import FEATURE_COLS_CLASSIFIER, FEATURE_COLS_REGRESSOR

print(f"Classifier features ({len(FEATURE_COLS_CLASSIFIER)}): {FEATURE_COLS_CLASSIFIER}")
print(f"Regressor features ({len(FEATURE_COLS_REGRESSOR)}): {FEATURE_COLS_REGRESSOR}")

# Verify counts
assert len(FEATURE_COLS_CLASSIFIER) == 10, "Classifier should have 10 features"
assert len(FEATURE_COLS_REGRESSOR) == 9, "Regressor should have 9 features"

# Verify Tool wear in classifier but not regressor
assert 'Tool wear [min]' in FEATURE_COLS_CLASSIFIER, "Classifier missing wear"
assert 'Tool wear [min]' not in FEATURE_COLS_REGRESSOR, "Regressor shouldn't use wear (leakage)"

print("✓ Feature columns verified")
```

**Pass Criteria:** Feature counts and composition correct

---

## Full Validation Checklist

### Data & Models
- [ ] Both CSV files exist and have correct dimensions
- [ ] Raw data wear range: [0, 253] min
- [ ] Scaled data wear range: [-2, +2] normalized
- [ ] Both model pkl files exist (>500 KB each)
- [ ] Models load without errors
- [ ] Feature columns match (10 classifier, 9 regressor)

### Predictions
- [ ] Predictions vary across machines (not constant 5.3)
- [ ] Wear values in [0, 253] range
- [ ] RUL calculated correctly (= 253 - wear)
- [ ] Failure probabilities vary [0, 1]
- [ ] Errors < 2 min on average

### Web App
- [ ] Flask starts without errors
- [ ] Dashboard loads and displays 10 machines
- [ ] Color-coding correct (red/yellow/green by risk)
- [ ] All API endpoints respond with valid JSON
- [ ] No JavaScript errors in browser console

### Integration
- [ ] Predictions from API match dashboard display
- [ ] Stats API shows correct counts
- [ ] Machine details API returns expected fields
- [ ] RUL = 253 - wear (consistent across all displays)

---

## Automated Test Script

**File:** `web_app/verify_fix.py`

**What it does:**
1. Loads both raw and scaled CSV files
2. Compares data distributions
3. Loads XGBoost regressor model
4. Tests predictions on 5 random machines with known actual wear
5. Analyzes prediction variation
6. Returns PASS/FAIL with diagnostic info

**Run it:**
```bash
cd web_app
python verify_fix.py
```

**Output examples:**

**If working correctly:**
```
✓ Data files found
✓ Data distributions verified
  Raw data wear range: 0.0 - 253.0
  Scaled data wear range: -1.68 - 1.60
✓ Model loaded successfully
✓ Predictions vary across machines
  Min prediction: 5.1 min
  Max prediction: 240.3 min
  Std Dev: 78.4 min
  
✓ SUCCESS: Fix is working correctly!
```

**If still broken:**
```
✗ Predictions still constant at 5.3 min
✗ All predictions identical
✗ FAILED: Feature scale mismatch still present
  Check: features_engineered_raw.csv is loaded in app.py line 36
```

---

## Expected Performance After Fix

| Metric | Before Fix | After Fix | Status |
|--------|-----------|-----------|--------|
| Wear predictions | All 5.3 min | 5-240 min vary | ✓ Fixed |
| RUL predictions | All 248 min | 13-248 min vary | ✓ Fixed |
| Prediction error | 0-245 min | <2 min avg | ✓ Fixed |
| Classifier (risk) | Varies correctly | Still varies correctly | ✓ Still good |
| Dashboard display | Useless (all same) | Actionable (all diff) | ✓ Fixed |

---

## Troubleshooting Tests

**If predictions still constant:**
```bash
# Check what data is being loaded
grep "features_engineered" web_app/app.py

# Should show: ...features_engineered_raw.csv
# If shows: ...features_engineered_scaled.csv → Fix not applied!
```

**If API returns NaN:**
```python
import pandas as pd
df = pd.read_csv('data/processed/features_engineered_raw.csv')
print(df.isnull().sum())  # Should all be 0
```

**If model prediction logic seems wrong:**
```python
# Test with known values from training data
import numpy as np
from src.data.make_dataset import load_data

X_train, y_classifier, y_regressor = load_data()
pred = regressor.predict(X_train[:5])
print(f"Sample predictions: {pred}")  # Should vary, not all same
```

---

## Sign-Off Checklist

When everything passes:
- [ ] Quick verification: ✓ PASS
- [ ] Comprehensive validation: ✓ PASS
- [ ] Full checklist: ✓ All items checked
- [ ] verify_fix.py: ✓ SUCCESS
- [ ] Dashboard working: ✓ Verified
- [ ] API endpoints: ✓ All respond
- [ ] Model accuracy: ✓ Within spec (<2 min error)

**Status:** 🟢 **PRODUCTION READY**

---

**Last Updated:** February 22, 2026  
**Version:** 2.0  
**Maintenance:** Review after any code changes to app.py
