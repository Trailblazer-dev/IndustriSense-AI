# 🔧 ML Troubleshooting & Debugging Guide

Complete debugging resource for common ML pipeline issues in IndustriSense-AI.

---

## ⚡ Quick Diagnosis: The Feature Scale Mismatch

### Symptom: Constant Predictions
**All machines show the same wear prediction (e.g., 5.3 min regardless of actual values)**

### Root Cause
The XGBoost regressor was **trained on RAW data** but receives **SCALED data** at inference:

```
Training:  Raw features with ranges [0-253] for wear, [15000-20000] for stress
Inference: Scaled features with ranges [-1.68 to +1.60] (StandardScaler normalized)

Result: Tree splits learned on raw ranges don't match scaled input ranges
→ Trees can't make decisions → Default to training mean (≈5.3 min)
```

### The Fix (1 Line)
File: `web_app/app.py` Line 36

```python
# BEFORE (broken):
df = pd.read_csv(os.path.join(data_dir, 'features_engineered_scaled.csv'))

# AFTER (fixed):
df = pd.read_csv(os.path.join(data_dir, 'features_engineered_raw.csv'))
```

### Why This Works
- XGBoost trees are based on learned split thresholds (e.g., "if wear > 50, predict high")
- These thresholds are learned on **training data ranges**
- At inference, data must be in the **same scale** to trigger splits correctly
- Using raw data ensures feature ranges match what the model learned

---

## Symptom: Predictions Vary But Errors Are Huge (50+ min)

### Likely Cause: Feature Engineering Mismatch

**Check:**
1. Are interaction terms calculated correctly?
   ```python
   # Should match training Notebook 2
   df['Stress Index'] = df['Torque [Nm]'] * df['Tool wear [min]']
   df['Temp Diff [K]'] = df['Process temperature [K]'] - df['Air temperature [K]']
   ```

2. Is Anomaly Score generated the same way?
   ```python
   # Training used Isolation Forest on raw sensor data
   # Inference should use the SAME fitted IsoForest object
   ```

3. Feature order matches?
   ```python
   # Training order (Notebook 4, line 92):
   feature_cols = ['Air temp', 'Process temp', 'RPM', 'Torque', ...]
   
   # Inference order (app.py):
   FEATURE_COLS_REGRESSOR = ['Air temp', 'Process temp', 'RPM', ...]
   # Must be IDENTICAL
   ```

---

## Symptom: Model Loading Fails

### Error: `FileNotFoundError: xgboost_wear_regressor.pkl`

**Fix:**
1. Verify files exist:
   ```bash
   ls -la src/models/
   ```
   Should see: `xgboost_classifier.pkl` and `xgboost_wear_regressor.pkl`

2. Check path in `web_app/app.py`:
   ```python
   MODEL_DIR = '../src/models/'  # Relative to web_app/
   ```

3. Verify permissions:
   ```bash
   # Windows: File manager (right-click → Properties)
   # macOS/Linux: ls -l # Should show read permission
   ```

---

## Symptom: Classifier Works but Regressor Doesn't

### Check These Steps

**Step 1: Data Loading**
```python
# Add to app.py for debugging:
df = load_data()
print(f"Data shape: {df.shape}")
print(f"Features: {df.columns.tolist()}")
print(f"Wear range: {df['Tool wear [min]'].min()}-{df['Tool wear [min]'].max()}")
```

**Expected output:**
```
Data shape: (10000, 16)
Features: ['Air temperature [K]', 'Process temperature [K]', ...]
Wear range: 0.0-253.0  ← RAW data, not scaled!
```

**Step 2: Feature Extraction**
```python
# Debug feature selection
X_regressor = row[FEATURE_COLS_REGRESSOR].values.reshape(1, -1)
print(f"Features shape: {X_regressor.shape}")  # Should be (1, 9)
print(f"Feature values: {X_regressor[0]}")     # Should be raw scale

# Check for NaN
if np.isnan(X_regressor).any():
    print("ERROR: NaN values in features!")
```

**Step 3: Model Prediction**
```python
# Test prediction
prediction = regressor.predict(X_regressor)[0]
print(f"Prediction: {prediction}")

# Expected range: 0-253 minutes
# IF you see: -0.32, 0.15, 1.41, etc. → Data is SCALED (still broken)
# IF you see: 42.3, 180.1, 5.2, etc.  → Data is RAW (correct)
```

---

## Symptom: NaN or Invalid Values

### Check Data Integrity

```python
# In app.py, add to dashboard route:
df = load_data()

# Check for missing values
print(f"Missing values:\n{df.isnull().sum()}")

# Check data types
print(f"Data types:\n{df.dtypes}")

# Check value ranges
print(f"Feature ranges:\n{df[FEATURE_COLS_REGRESSOR].describe()}")
```

**Expected:**
- No NaN values
- All numeric types (int64, float64)
- Wear range: [0, 253]
- Temperature range: [295, 320]
- Other features in expected bounds

### If NaN Found
```python
# Remove or fill
df = df.dropna()  # Remove rows with NaN
# OR
df = df.fillna(df.mean())  # Fill with mean
```

---

## Symptom: XGBoost Not Installed

### Error: `ModuleNotFoundError: No module named 'xgboost'`

**Fix:**
```bash
pip install xgboost
# or
pip install -r web_app/requirements.txt
```

---

## Symptom: Cross-Tab Verification (For Debuggers)

### Did data get mixed between training and inference?

**Check during training (Notebook 4):**
```python
# Line 58
df_train = pd.read_csv('../data/processed/features_engineered_raw.csv')
print(f"Train data source: RAW, wear range = {df_train['Tool wear [min]'].min()}-{df_train['Tool wear [min]'].max()}")
# Output: RAW, wear range = 0.0-253.0 ✓
```

**Check during inference (app.py):**
```python
def load_data():
    df = pd.read_csv(os.path.join(data_dir, 'features_engineered_raw.csv'))  # Fixed ✓
    print(f"Inference data source: RAW, wear range = {df['Tool wear [min]'].min()}-{df['Tool wear [min]'].max()}")
    # Should also output: RAW, wear range = 0.0-253.0 ✓
```

**If wear range is [-1.68 to +1.60]:** ❌ Still using scaled data. Check your fix was applied.

---

## Performance Expectations

### After Fix Applied Correctly

**Regression Model Accuracy:**
```
Training R²:  0.9996 (excellent)
Test MAE:     0.88 min (excellent)
Test RMSE:    1.37 min (excellent)

After fix Applied:
Inference Errors should be <2 min for most predictions
```

**Example Predictions:**
```
Machine 1: Actual=198 min, Predicted=195.3 min, Error=2.7 min (1.4%)  ✓
Machine 2: Actual=101 min, Predicted=100.8 min, Error=0.2 min (0.2%)  ✓
Machine 3: Actual=117 min, Predicted=119.4 min, Error=2.4 min (2.0%)  ✓
```

**Classifier Accuracy:**
```
Failure Risk: Varies 0-100% across machines ✓
Not all the same probability ✓
```

---

## Debugging Checklist

- [ ] Verified data file exists: `data/processed/features_engineered_raw.csv`
- [ ] Confirmed app.py loads raw.csv (line 36)
- [ ] Restarted Flask after code changes
- [ ] Cleared browser cache (Ctrl+Shift+Delete)
- [ ] Feature ranges match training expectations (raw, not scaled)
- [ ] No NaN values in loaded data
- [ ] Model files exist and are readable
- [ ] Predictions vary (not all ~5.3)
- [ ] RUL calculated as 253 - wear (correct formula)
- [ ] Error margins reasonable (<2 min for wear)

---

## Common Fixes (Ranked by Likelihood)

1. **Load raw.csv instead of scaled.csv** (99% chance if constant 5.3 predictions)
2. **Restart Flask** (99% chance if code changed but not applied)
3. **Clear browser cache** (90% chance if strange display issues)
4. **Feature engineering mismatch** (70% chance if errors are huge)
5. **Data type issues** (50% chance if weird behavior)
6. **Model loading path** (20% chance if FileNotFoundError)

---

## Advanced: Understanding XGBoost Tree Splits

### Why Scaling Breaks XGBoost

**During training, XGBoost learns splits like this:**

```
Feature: Stress Index  (Range in training data: [0, 19228])

Tree Split Learned:
  if stress_index <= 5000:
    predict low_wear
  else:
    predict high_wear

Actual training sample:
  stress_index = 8500 → Falls into "high_wear" branch ✓
```

**At inference with SCALED data:**

```
Same tree split still exists: if stress_index <= 5000

But now we get scaled values: stress_index = 0.42

Does 0.42 <= 5000? YES!
→ Tree takes "low_wear" branch
→ Wrong answer!
```

**At inference with RAW data:**

```
Same tree split: if stress_index <= 5000

Raw value: stress_index = 8500

Does 8500 <= 5000? NO!
→ Tree takes "high_wear" branch  
→ Correct answer! ✓
```

---

## Related Documentation

- [Verification Checklist](verification.md) - Testing and validation
- [Quick Start](../guides/quick-start.md) - Getting started
- [ML Pipeline Architecture](../architecture/ml-pipeline.md) - Detailed design
- [Web App Docs](web-app.md) - Flask application reference

---

**Last Updated:** February 22, 2026  
**Confidence Level:** 99% for constant prediction fixes  
**Version:** 2.0
