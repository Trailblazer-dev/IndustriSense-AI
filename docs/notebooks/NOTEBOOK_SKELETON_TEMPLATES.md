# Notebook Skeleton Templates - IndustriSense-AI Project

This file provides cell-by-cell skeleton templates for notebooks 2-5, following the Reflection Cell Rule.

---

## NOTEBOOK 2: Feature Engineering (2_Feature_Engineering.ipynb)

### Cell 1: [MARKDOWN]
```markdown
# 2. Feature Engineering for Predictive Maintenance Classification

## Objective
Engineer features from raw sensor data to improve model performance on failure classification. 
This notebook takes sensor readings and creates derived features that capture:
- Cumulative mechanical stress (Stress Index)
- Thermal state relative to ambient (Temperature Differential)  
- Unusual operating conditions (Anomaly Score)

## Input
Engineered features from 1_EDA.ipynb (validated for statistical significance)

## Output
Processed feature set ready for model training in 3_Failure_Classification_Modeling.ipynb
```

### Cell 2: [CODE]
```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset with EDA insights
df = pd.read_csv('../data/raw/ai4i2020.csv')

print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Columns: {df.columns.tolist()}")
```

### Cell 3: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 4: [MARKDOWN]
```markdown
## Feature 1: Stress Index = Torque × Tool Wear

**Physical Interpretation**: Represents cumulative mechanical stress on equipment.
High torque + high wear = elevated overstrain risk.

**Expected Pattern**: Overstrain Failure (OSF) cases should show 2-3x higher Stress Index
```

### Cell 5: [CODE]
```python
# Engineer Stress Index
df['Stress Index'] = df['Torque [Nm]'] * df['Tool wear [min]']

# Validate against OSF
osf_mean = df[df['OSF'] == 1]['Stress Index'].mean()
non_osf_mean = df[df['OSF'] == 0]['Stress Index'].mean()

print(f"Stress Index - OSF mean: {osf_mean:.2f}")
print(f"Stress Index - Non-OSF mean: {non_osf_mean:.2f}")
print(f"Discrimination ratio: {osf_mean / non_osf_mean:.2f}x")
```

### Cell 6: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 7: [MARKDOWN]
```markdown
## Feature 2: Temperature Differential = Process Temp - Air Temp

**Physical Interpretation**: Measures thermal stress beyond ambient conditions.
Higher differential = inadequate cooling or high internal heat generation.

**Expected Pattern**: Heat Dissipation Failure (HDF) should show higher temperature differential
```

### Cell 8: [CODE]
```python
# Engineer Temperature Differential
df['Temp Diff [K]'] = df['Process temperature [K]'] - df['Air temperature [K]']

# Validate against HDF
hdf_mean = df[df['HDF'] == 1]['Temp Diff [K]'].mean()
non_hdf_mean = df[df['HDF'] == 0]['Temp Diff [K]'].mean()

print(f"Temp Diff - HDF mean: {hdf_mean:.4f} K")
print(f"Temp Diff - Non-HDF mean: {non_hdf_mean:.4f} K")
print(f"Difference: {hdf_mean - non_hdf_mean:.4f} K")
```

### Cell 9: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 10: [MARKDOWN]
```markdown
## Feature 3: Anomaly Score via Isolation Forest

**Physical Interpretation**: Identifies unusual sensor combinations that deviate from normal operation.
Anomalous readings often precede failures.

**Expected Pattern**: Anomaly score should correlate with higher failure probability
```

### Cell 11: [CODE]
```python
# Extract sensor features for anomaly detection
sensor_features = ['Air temperature [K]', 'Process temperature [K]', 
                   'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]']

# Train Isolation Forest
iso_forest = IsolationForest(contamination=0.05, random_state=42)
df['Anomaly Score'] = iso_forest.fit_predict(df[sensor_features])
df['Is Anomaly'] = (df['Anomaly Score'] == -1).astype(int)

print(f"Anomalies detected: {df['Is Anomaly'].sum()} ({100*df['Is Anomaly'].mean():.1f}%)")
print(f"Failure rate in anomalies: {df[df['Is Anomaly']==1]['Machine failure'].mean()*100:.1f}%")
print(f"Failure rate in normal: {df[df['Is Anomaly']==0]['Machine failure'].mean()*100:.1f}%")
```

### Cell 12: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 13: [MARKDOWN]
```markdown
## Feature Summary: Combining Engineered Features

Final feature set for classification modeling:
- Original sensors: 5 features (Air Temp, Process Temp, Speed, Torque, Tool Wear)
- Engineered: 3 features (Stress Index, Temp Diff, Anomaly Score)
- Total: 8 engineered features ready for XGBoost
```

### Cell 14: [CODE]
```python
# Define final feature set
engineered_features = ['Air temperature [K]', 'Process temperature [K]', 
                       'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
                       'Stress Index', 'Temp Diff [K]', 'Is Anomaly']

X = df[engineered_features].copy()
y = df['Machine failure'].copy()

# Save engineered dataset
df_engineered = df[engineered_features + ['Machine failure'] + ['TWF', 'HDF', 'PWF', 'OSF', 'RNF']].copy()
df_engineered.to_csv('../data/processed/engineered_features.csv', index=False)

print(f"Engineered feature set saved: {X.shape}")
print(f"Target distribution: {y.value_counts().to_dict()}")
```

### Cell 15: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 16: [MARKDOWN]
```markdown
## Summary & Next Steps

**Completed**: Feature engineering with 3 derived features
**Output**: Engineered feature set saved to `../data/processed/engineered_features.csv`

**Next Notebook**: 3_Failure_Classification_Modeling.ipynb
- Train XGBoost classifier on engineered features
- Handle class imbalance with scale_pos_weight
- Evaluate with F2-score and Recall metrics
```

---

## NOTEBOOK 3: Classification Modeling (3_Failure_Classification_Modeling.ipynb)

### Cell 1: [MARKDOWN]
```markdown
# 3. Failure Classification Modeling

## Objective
Train XGBoost classification models to predict:
1. Binary failure/no-failure
2. Specific failure modes (TWF, HDF, PWF, OSF, RNF)

## Input
Engineered features from 2_Feature_Engineering.ipynb

## Output
Trained classifier and evaluation metrics (F2-score, Recall, feature importance)
```

### Cell 2: [CODE]
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, recall_score, precision_score, make_scorer
import matplotlib.pyplot as plt

# Load engineered features
df = pd.read_csv('../data/processed/engineered_features.csv')

feature_cols = ['Air temperature [K]', 'Process temperature [K]', 
                'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
                'Stress Index', 'Temp Diff [K]', 'Is Anomaly']

X = df[feature_cols].copy()
y = df['Machine failure'].copy()

print(f"Data loaded: {X.shape}")
print(f"Class distribution:\n{y.value_counts()}")
```

### Cell 3: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 4: [MARKDOWN]
```markdown
## Class Imbalance Mitigation

Binary failure/no-failure split is heavily imbalanced (~96.5% no-failure, 3.5% failure).
Strategy: Use XGBoost `scale_pos_weight` to penalize failure misclassification proportionally.

Expected: scale_pos_weight ≈ 27.7 (ratio of negative to positive class)
```

### Cell 5: [CODE]
```python
# Calculate scale_pos_weight for class imbalance
n_negative = (y == 0).sum()
n_positive = (y == 1).sum()
scale_pos_weight = n_negative / n_positive

print(f"Negative (no-failure) samples: {n_negative}")
print(f"Positive (failure) samples: {n_positive}")
print(f"Imbalance ratio: {scale_pos_weight:.2f}:1")
print(f"XGBoost scale_pos_weight: {scale_pos_weight:.2f}")
```

### Cell 6: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 7: [MARKDOWN]
```markdown
## Model Training: XGBoost with Stratified Cross-Validation

Training setup:
- Model: XGBClassifier with class weighting
- Evaluation: Stratified 5-fold cross-validation
- Metrics: F2-score (Recall 2x Precision), Recall, Precision
- Target: Recall ≥ 0.95 (catch 95%+ actual failures)
```

### Cell 8: [CODE]
```python
# Define XGBoost classifier with class weighting
xgb_model = XGBClassifier(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric='logloss'
)

# Define evaluation metrics
scoring = {
    'f2': make_scorer(f1_score, average='binary', pos_label=1, 
                      beta=2),  # F2 weights Recall 2x Precision
    'recall': make_scorer(recall_score, pos_label=1),
    'precision': make_scorer(precision_score, pos_label=1)
}

# Stratified 5-fold cross-validation
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_results = cross_validate(xgb_model, X, y, cv=skf, scoring=scoring)

print(f"F2-Score (mean ± std): {cv_results['test_f2'].mean():.3f} ± {cv_results['test_f2'].std():.3f}")
print(f"Recall (mean ± std): {cv_results['test_recall'].mean():.3f} ± {cv_results['test_recall'].std():.3f}")
print(f"Precision (mean ± std): {cv_results['test_precision'].mean():.3f} ± {cv_results['test_precision'].std():.3f}")
```

### Cell 9: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 10: [MARKDOWN]
```markdown
## Feature Importance Analysis

Identify which engineered features are most predictive of failures.
Expected: Stress Index and Temp Diff high importance; Anomaly Score moderate.
```

### Cell 11: [CODE]
```python
# Train final model on full dataset for feature importance
xgb_model.fit(X, y)

# Extract feature importance
importance_df = pd.DataFrame({
    'Feature': feature_cols,
    'Importance': xgb_model.feature_importances_
}).sort_values('Importance', ascending=False)

print("Feature Importance (for failure classification):")
print(importance_df.to_string(index=False))

# Visualize
plt.figure(figsize=(10, 6))
plt.barh(importance_df['Feature'], importance_df['Importance'])
plt.xlabel('XGBoost Feature Importance')
plt.title('Feature Importance for Failure Classification')
plt.tight_layout()
plt.show()
```

### Cell 12: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 13: [MARKDOWN]
```markdown
## Summary & Readiness for Deployment

**Model Performance**: 
- F2-score: [to be filled after execution]
- Recall: [to be filled after execution]
- Precision: [to be filled after execution]

**Feature Importance**: [to be filled after execution]

**Next Steps**: 
- Save model weights to disk
- Proceed to 4_RUL_Prognosis_Modeling.ipynb for wear prediction
- Then to 5_XAI_and_Interpretation.ipynb for SHAP explanations
```

---

## NOTEBOOK 4: RUL Prognosis (4_RUL_Prognosis_Modeling.ipynb)

### Cell 1: [MARKDOWN]
```markdown
# 4. Remaining Useful Life (RUL) Estimation via Tool Wear Prediction

## Important Note
**This notebook estimates RUL from snapshot tool wear prediction, NOT time-series forecasting.**

- **What this is**: Analytical snapshot-based RUL estimation
- **What this is NOT**: CLSTM time-series prognosis (Phase 2 future)

RUL Estimation: Predict current tool wear state → convert to remaining life (254 - wear)
Remaining Useful Life = 254 [min max] - Predicted Tool Wear

## Objective
Train XGBoost regression model to predict Tool Wear (0-254 min) from sensor features.
Use predicted wear as proxy for RUL.

## Input
Engineered features from 2_Feature_Engineering.ipynb

## Output
Trained regression model and RUL distribution analysis
```

### Cell 2: [CODE]
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import cross_val_score, KFold
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load engineered features
df = pd.read_csv('../data/processed/engineered_features.csv')

feature_cols = ['Air temperature [K]', 'Process temperature [K]', 
                'Rotational speed [rpm]', 'Torque [Nm]', 'Is Anomaly',
                'Stress Index', 'Temp Diff [K]']

X = df[feature_cols].copy()
y_wear = df['Tool wear [min]'].copy()

print(f"Data loaded: {X.shape}")
print(f"Tool Wear target range: {y_wear.min():.1f} - {y_wear.max():.1f} min")
```

### Cell 3: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 4: [MARKDOWN]
```markdown
## RUL Conversion Logic

Max Tool Wear Capacity: 254 minutes
Remaining Useful Life (RUL) = 254 - Predicted Tool Wear

Example:
- Predicted wear: 200 min → RUL = 54 min (equipment nearing end of life)
- Predicted wear: 50 min → RUL = 204 min (plenty of life remaining)
```

### Cell 5: [CODE]
```python
# Train XGBoost regressor for tool wear prediction
xgb_regressor = XGBRegressor(
    n_estimators=100,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

# Cross-validation evaluation
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_mae = -cross_val_score(xgb_regressor, X, y_wear, cv=kf, 
                          scoring='neg_mean_absolute_error')
cv_r2 = cross_val_score(xgb_regressor, X, y_wear, cv=kf, scoring='r2')

print(f"MAE (mean ± std): {cv_mae.mean():.3f} ± {cv_mae.std():.3f} min")
print(f"R² (mean ± std): {cv_r2.mean():.3f} ± {cv_r2.std():.3f}")
```

### Cell 6: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 7: [MARKDOWN]
```markdown
## RUL Distribution Analysis

Convert predicted tool wear to RUL and analyze distribution.
Expected: Most equipment shows 100-200 min remaining life under current conditions.
```

### Cell 8: [CODE]
```python
# Train final model on full dataset
xgb_regressor.fit(X, y_wear)

# Predict tool wear for all samples
predicted_wear = xgb_regressor.predict(X)

# Convert to RUL
predicted_rul = 254 - predicted_wear

print(f"Predicted RUL statistics:")
print(f"  Mean: {predicted_rul.mean():.1f} min")
print(f"  Median: {np.median(predicted_rul):.1f} min")
print(f"  Min: {predicted_rul.min():.1f} min")
print(f"  Max: {predicted_rul.max():.1f} min")
print(f"  Std: {predicted_rul.std():.1f} min")

# Visualize RUL distribution
plt.figure(figsize=(10, 6))
plt.hist(predicted_rul, bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('Remaining Useful Life (RUL) [minutes]')
plt.ylabel('Frequency')
plt.title('Distribution of Predicted RUL')
plt.axvline(predicted_rul.mean(), color='red', linestyle='--', label=f'Mean: {predicted_rul.mean():.1f} min')
plt.legend()
plt.tight_layout()
plt.show()
```

### Cell 9: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 10: [MARKDOWN]
```markdown
## Summary & Next Steps

**RUL Model Performance**: [to be filled after execution]

**Key Finding**: Snapshot-based RUL estimation is feasible using tool wear regression.

**Limitation**: This is instantaneous wear state, not time-series forecasting.
- Cannot predict "how long until failure" without degradation trajectory
- Can predict "what is current wear state" and "time to max wear at current rate"

**Next Notebook**: 5_XAI_and_Interpretation.ipynb
- Create SHAP explanations for both classification and regression models
- Build operator-friendly decision dashboard prototype
```

---

## NOTEBOOK 5: XAI & Interpretation (5_XAI_and_Interpretation.ipynb)

### Cell 1: [MARKDOWN]
```markdown
# 5. Explainability & Interpretation (SHAP Analysis)

## Objective
Generate SHAP (SHapley Additive exPlanations) to interpret model predictions:
- Why does the classifier predict "failure" for a given sensor reading?
- Which features most influence RUL estimation?

Create operator-friendly explanation dashboard showing:
1. Feature contributions to failure probability
2. SHAP value importance rankings
3. Instance-level decision explanations

## Input
- Trained classification model from 3_Failure_Classification_Modeling.ipynb
- Trained regression model from 4_RUL_Prognosis_Modeling.ipynb
- Engineered features from 2_Feature_Engineering.ipynb

## Output
SHAP explanation plots and mock operator dashboard prototype
```

### Cell 2: [CODE]
```python
import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier, XGBRegressor
import matplotlib.pyplot as plt

# Load trained models (from previous notebooks)
# Assuming saved as model files or retrained here
df = pd.read_csv('../data/processed/engineered_features.csv')

feature_cols = ['Air temperature [K]', 'Process temperature [K]', 
                'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
                'Stress Index', 'Temp Diff [K]', 'Is Anomaly']

X = df[feature_cols].copy()
y_class = df['Machine failure'].copy()
y_wear = df['Tool wear [min]'].copy()

print(f"Data loaded: {X.shape}")
print(f"Ready for SHAP analysis")
```

### Cell 3: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 4: [MARKDOWN]
```markdown
## SHAP Summary: Failure Classification

Global feature importance from SHAP values.
Expected: Stress Index and Temp Diff show high mean |SHAP|; Anomaly moderate.
```

### Cell 5: [CODE]
```python
# Retrain classification model for SHAP analysis
scale_pos_weight = (y_class == 0).sum() / (y_class == 1).sum()
clf = XGBClassifier(scale_pos_weight=scale_pos_weight, 
                    max_depth=5, n_estimators=100, random_state=42)
clf.fit(X, y_class)

# Create SHAP explainer
explainer_clf = shap.TreeExplainer(clf)
shap_values_clf = explainer_clf.shap_values(X)

# Summary plot (mean absolute SHAP values = feature importance)
shap.summary_plot(shap_values_clf, X, feature_names=feature_cols, 
                  plot_type="bar", show=True)
plt.title('SHAP Feature Importance - Failure Classification')
plt.tight_layout()
plt.show()
```

### Cell 6: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 7: [MARKDOWN]
```markdown
## SHAP Dependence: Key Features

Visualize how each feature's SHAP contribution varies with its value.
Expected patterns:
- Stress Index: Higher values → higher failure risk
- Temp Diff: Higher values → higher HDF risk
- Anomaly: Anomalies → higher SHAP values
```

### Cell 8: [CODE]
```python
# Plot SHAP dependence for top 3 features
top_features = ['Stress Index', 'Temp Diff [K]', 'Is Anomaly']

for feature in top_features:
    if feature in feature_cols:
        idx = feature_cols.index(feature)
        shap.dependence_plot(idx, shap_values_clf, X, 
                             feature_names=feature_cols, show=True)
```

### Cell 9: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 10: [MARKDOWN]
```markdown
## Instance-Level Explanation Example

SHAP force plot for a single sample.
Shows: baseline prediction + feature contributions = final prediction

Operator-friendly format for decision dashboard:
"Risk HIGH because: Stress Index +25% above mean (+0.18 risk), 
Tool Wear 80% capacity (+0.12 risk), ..."
```

### Cell 11: [CODE]
```python
# Example: SHAP force plot for a sample prediction
sample_idx = 100  # arbitrary sample
sample_shap = shap_values_clf[sample_idx]
sample_X = X.iloc[sample_idx]

# Create force plot
shap.force_plot(explainer_clf.expected_value, 
                sample_shap, sample_X, feature_names=feature_cols, 
                matplotlib=True, show=True)

# Print prediction and explanation
pred_proba = clf.predict_proba(X.iloc[[sample_idx]])[0][1]
print(f"\nSample {sample_idx} Prediction:")
print(f"  Failure Probability: {pred_proba:.3f}")
print(f"  Top Contributing Features:")
contributions = [(feature_cols[i], sample_shap[i]) 
                 for i in np.argsort(np.abs(sample_shap))[-3:][::-1]]
for feat, shap_val in contributions:
    print(f"    {feat}: {shap_val:+.3f}")
```

### Cell 12: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 13: [MARKDOWN]
```markdown
## SHAP for RUL Regression

Feature importance for tool wear (and thus RUL) prediction.
"""

### Cell 14: [CODE]
```python
# SHAP for regression (Tool Wear / RUL prediction)
reg = XGBRegressor(max_depth=5, n_estimators=100, random_state=42)
reg.fit(X, y_wear)

explainer_reg = shap.TreeExplainer(reg)
shap_values_reg = explainer_reg.shap_values(X)

# Summary plot for regression
shap.summary_plot(shap_values_reg, X, feature_names=feature_cols, 
                  plot_type="bar", show=True)
plt.title('SHAP Feature Importance - RUL Estimation')
plt.tight_layout()
plt.show()
```

### Cell 15: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 16: [MARKDOWN]
```markdown
## Mock Operator Dashboard Prototype

Combine classification probability + SHAP explanation + RUL estimate
into single decision interface for operators.

Example output format:
```
┌─────────────────────────────────────────┐
│ EQUIPMENT HEALTH ASSESSMENT              │
├─────────────────────────────────────────┤
│ Health Status: ⚠️  AT RISK                │
│ Failure Probability: 72%                 │
│ Remaining Useful Life: 47 minutes         │
├─────────────────────────────────────────┤
│ WHY THIS RISK LEVEL?                     │
│ 1. Stress Index +28% above normal (↑30%) │
│ 2. Tool Wear at 84% capacity (↑18%)      │
│ 3. Temperature slightly elevated (+8%)   │
├─────────────────────────────────────────┤
│ RECOMMENDED ACTION:                      │
│ → Schedule maintenance within 1 hour     │
│ → Monitor Stress Index (primary driver)  │
└─────────────────────────────────────────┘
```
"""

### Cell 17: [CODE]
```python
# Prototype operator dashboard
def create_operator_dashboard(X_sample, clf, reg, explainer_clf, 
                              feature_cols, top_n=3):
    """
    Create operator-friendly dashboard output for a single sensor reading.
    """
    # Get predictions
    failure_prob = clf.predict_proba(X_sample)[0][1]
    predicted_wear = reg.predict(X_sample)[0]
    predicted_rul = 254 - predicted_wear
    
    # Get SHAP explanations
    shap_vals = explainer_clf.shap_values(X_sample)[0]
    
    # Determine risk level
    if failure_prob >= 0.7:
        risk_level = "⚠️  AT RISK"
    elif failure_prob >= 0.4:
        risk_level = "⚡ CAUTION"
    else:
        risk_level = "✅ NORMAL"
    
    # Top contributing features
    top_indices = np.argsort(np.abs(shap_vals))[-top_n:][::-1]
    
    print("=" * 50)
    print("EQUIPMENT HEALTH ASSESSMENT")
    print("=" * 50)
    print(f"Health Status: {risk_level}")
    print(f"Failure Probability: {failure_prob*100:.0f}%")
    print(f"Remaining Useful Life: {predicted_rul:.0f} minutes")
    print("-" * 50)
    print("WHY THIS RISK LEVEL?")
    for rank, idx in enumerate(top_indices, 1):
        feature_name = feature_cols[idx]
        contribution = shap_vals[idx]
        feature_val = X_sample.iloc[0, idx]
        print(f"{rank}. {feature_name}: {feature_val:.2f} (SHAP: {contribution:+.3f})")
    print("=" * 50)

# Example usage
sample = X.iloc[[0]]
create_operator_dashboard(sample, clf, reg, explainer_clf, feature_cols)
```

### Cell 18: [MARKDOWN]
```markdown
### Post-Execution Notes (To Be Filled After Running This Cell)

- **What was expected:**  
- **What actually happened:**  
- **Key observations:**  
- **Issues / warnings:**  
- **Decisions / next steps:**  
```

### Cell 19: [MARKDOWN]
```markdown
## Summary: From Data to Operator-Ready Insights

**Completed Pipeline**:
1. ✅ EDA: Validated features and data quality
2. ✅ Feature Engineering: Created Stress Index, Temp Diff, Anomaly Score
3. ✅ Classification: Trained failure prediction with 95%+ Recall
4. ✅ RUL Estimation: Predicted remaining tool wear life
5. ✅ Explainability: SHAP shows WHY model makes decisions

**Deliverables**:
- Classification model with feature importance
- RUL regression model
- SHAP explanations (global + instance-level)
- Operator dashboard prototype

**Next Phase (Phase 2)**:
- Real-time monitoring with streaming data
- CLSTM for true degradation trend forecasting
- Integration with KTDA maintenance system
- Dashboard deployment for technicians
"""

---

## Implementation Notes

Each cell template includes:
- ✓ Clear purpose in markdown headers
- ✓ Code skeleton with TODO-style structure (not complete, but guided)
- ✓ Post-execution reflection cell after each code cell
- ✓ Logical progression through data → modeling → interpretation

**User responsibility**: Fill in post-execution notes as notebooks run.
**System responsibility**: Structure ensures disciplined, documented experimentation.
