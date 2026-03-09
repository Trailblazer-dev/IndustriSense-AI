# 📔 Notebook Documentation

Guide to IndustriSense-AI Jupyter notebooks and best practices.

---

## 🎯 Notebooks Overview

The project includes **5 Jupyter notebooks** designed to be run in sequence:

| # | Notebook | Purpose | Time |
|---|----------|---------|------|
| 1 | [1_EDA.ipynb](../../notebooks/1_EDA.ipynb) | Exploratory Data Analysis | 15-20 min |
| 2 | [2_Feature_Engineering.ipynb](../../notebooks/2_Feature_Engineering.ipynb) | Feature Creation & Scaling | 15-20 min |
| 3 | [3_Failure_Classification_Modeling.ipynb](../../notebooks/3_Failure_Classification_Modeling.ipynb) | Failure Prediction Model | 20-30 min |
| 4 | [4_RUL_Prognosis_Modeling.ipynb](../../notebooks/4_RUL_Prognosis_Modeling.ipynb) | Tool Wear / RUL Estimation | 20-30 min |
| 5 | [5_XAI_and_Interpretation.ipynb](../../notebooks/5_XAI_and_Interpretation.ipynb) | SHAP Explainability Analysis | 15-20 min |

**Total time to run all:** ~2 hours

---

## 📈 Notebook 1: Exploratory Data Analysis (EDA)

**Purpose:** Understand the dataset and verify data quality

**What you'll do:**
- Load AI4I 2020 dataset (10,000 samples)
- Examine 16 features and target variables
- Check data types and missing values
- Visualize distributions and correlations
- Identify patterns and outliers

**Key outputs:**
- Feature statistics (mean, std, min/max)
- Correlation heatmap
- Distribution plots
- Missing value check

**Time:** ~15-20 minutes

**Start here if:** You want to understand the data

---

## 🔧 Notebook 2: Feature Engineering

**Purpose:** Create new features for better model predictions

**What you'll do:**
- Load raw AI4I 2020 data
- Create Stress Index (Torque × Tool Wear)
- Calculate Temperature Differential
- Generate Anomaly Score (Isolation Forest)
- Create interaction terms
- Scale features using StandardScaler

**Key outputs:**
- `features_engineered_raw.csv` — Raw engineered features (10,000 rows × 16 cols)
- `features_engineered_scaled.csv` — Scaled version (StandardScaler normalized)

**Features created:**
- Stress Index: Mechanical stress indicator
- Temp Diff: Thermal differential
- Temp_Diff_x_Wear: Interaction term  
- Speed_x_Torque: Interaction term
- is_anomaly: Binary anomaly flag

**Time:** ~15-20 minutes

**Start here if:** You want to understand feature engineering

---

## 🎯 Notebook 3: Failure Classification Modeling

**Purpose:** Predict if a machine will fail (binary classification)

**What you'll do:**
- Load engineered features
- Build XGBoost classifier
- Train on 8,000 samples with 5-fold cross-validation
- Evaluate on 2,000 held-out test samples
- Calculate feature importance
- Generate SHAP explanations

**Model specs:**
- Algorithm: XGBoost Classifier
- Input features: 10 (all engineered features)
- Target: Machine failure (0=no, 1=yes)
- Class balance: 3.5% failure rate

**Performance:**
- Accuracy: 98.8%
- F1-Score: 0.826
- ROC-AUC: 0.982
- Recall: 83.8%

**Key outputs:**
- `xgboost_classifier.pkl` — Trained model (saved)
- Feature importance rankings
- SHAP explanation plots

**Time:** ~20-30 minutes

**Start here if:** You want to understand classification

---

## 📊 Notebook 4: RUL Prognosis Modeling

**Purpose:** Estimate tool wear and remaining useful life

**What you'll do:**
- Load engineered features WITHOUT tool wear column (prevent leakage)
- Build XGBoost regressor (9 features)
- Train on 8,000 samples with 5-fold cross-validation
- Evaluate on 2,000 held-out test samples
- Calculate feature importance for wear prediction
- Analyze prediction errors

**Model specs:**
- Algorithm: XGBoost Regressor
- Input features: 9 (excludes tool wear to prevent target leakage)
- Target: Tool wear in minutes (0-253)
- Objective: Minimize squared error

**Performance:**
- Test R²: 0.9996 (excellent generalization!)
- Test MAE: 0.88 min (average error <1 min)
- Test RMSE: 1.37 min
- CV R² Mean: 0.9996 ± 0.000037 (very consistent)

**Key outputs:**
- `xgboost_wear_regressor.pkl` — Trained model (saved)
- Feature importance (Temp_Diff_x_Wear dominates at 71%)
- Error analysis plots

**Critical note:** This model is trained on **RAW data**. The Flask app MUST load raw.csv, not scaled.csv.

**Time:** ~20-30 minutes

**Start here if:** You want to understand regression

---

## 🔍 Notebook 5: XAI & Interpretation

**Purpose:** Understand model predictions using SHAP

**What you'll do:**
- Load trained models (classifier, regressor)
- Calculate SHAP values for predictions
- Create SHAP summary plots
- Generate individual prediction explanations
- Build interpretation guide for operators

**Outputs:**
- SHAP force plots (why prediction made)
- Summary plots (feature importance from SHAP)
- Interpretation guidelines
- Operator decision aid

**Time:** ~15-20 minutes

**Start here if:** You want to understand model decisions

---

## 📚 Documentation by Topic

### Notebook Architecture & Patterns
See: [architecture.md](architecture.md) — Design patterns and best practices

### Coding Standards
See: [standards.md](standards.md) — Code conventions and style guide

### Skeleton Templates
See: [templates.md](templates.md) — Boilerplate code templates

### ML Best Practices
See: [ml-best-practices.md](ml-best-practices.md) — ML pipeline patterns

### Train/Test Split Details
See: [train-test-split.md](train-test-split.md) — Data splitting methodology

---

## 🚀 How to Run Notebooks

### Prerequisites
```bash
# Activate virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# or
source venv/bin/activate       # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Launch Jupyter
```bash
jupyter notebook
```

Browser should open to `http://localhost:8888/`

### Run Notebooks
1. Open each notebook file (e.g., `1_EDA.ipynb`)
2. Run cells in order (Shift+Enter or play button)
3. Review outputs and analyze results
4. Modify parameters if desired for experimentation

### What Gets Created
- After Notebook 2: Feature CSV files in `data/processed/`
- After Notebook 3: Classifier model in `src/models/`
- After Notebook 4: Regressor model in `src/models/`
- After Notebook 5: Interpretation artifacts and guides

---

## 📊 Data Flow Through Notebooks

```
Raw Dataset
(AI4I 2020)
    ↓
[1_EDA.ipynb]
Exploratory analysis
    ↓
[2_Feature_Engineering.ipynb]
Create features + scale
    ├─→ features_engineered_raw.csv
    └─→ features_engineered_scaled.csv
    ↓
    ├─→ [3_Failure_Classification_Modeling.ipynb]
    │   Training: Features → Classifier
    │   Output: xgboost_classifier.pkl
    │
    └─→ [4_RUL_Prognosis_Modeling.ipynb]
        Training: Features (no target) → Regressor
        Output: xgboost_wear_regressor.pkl
    ↓
[5_XAI_and_Interpretation.ipynb]
SHAP explanations + interpretation guides
    ↓
Interpretable Predictions for Dashboard
```

---

## ⚠️ Important Notes

### About Data Scaling
- **Feature Engineering notebook** creates BOTH raw and scaled versions
- **Training notebooks** use RAW data only (not the scaled version)
- **Flask app** MUST load raw.csv (not scaled.csv) for correct inference
- See [../deployment/ml-troubleshooting.md](../deployment/ml-troubleshooting.md) if predictions are constant

### About Feature Engineering in Notebooks
- Notebooks 3 & 4 load pre-engineered features from CSV
- To modify features, edit **Notebook 2** and re-run all
- Changes won't apply until you re-run downstream notebooks

### About Model Serialization
- Models are pickled after training
- Always use `pickle.load()` in Flask app, not model recreation
- Models are deterministic (same predictions each run)

---

## 🔗 Related Documentation

- [Quick Start Guide](../guides/quick-start.md) — How to run notebooks
- [Architecture Patterns](architecture.md) — Notebook design patterns
- [ML Pipeline Details](../architecture/ml-pipeline.md) — Model specifications
- [Troubleshooting](../deployment/ml-troubleshooting.md) — Common issues

---

**Version:** 2.0  
**Last Updated:** February 22, 2026  
**Status:** Production Ready
