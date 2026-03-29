# 📔 Notebook Documentation

Technical reference for the IndustriSense AI data science pipeline.

---

## 🎯 Pipeline Overview

The project includes **5 Jupyter notebooks** that define the end-to-end analytical lifecycle:

| # | Notebook | Purpose | Core Technologies |
|---|----------|---------|-------------------|
| 1 | `1_EDA.ipynb` | Exploratory Data Analysis | Pandas, Seaborn |
| 2 | `2_Feature_Engineering.ipynb` | Interaction & Anomaly Generation | Scikit-Learn |
| 3 | `3_Failure_Classification.ipynb` | Failure Mode Prediction | XGBoost |
| 4 | `4_RUL_Prognosis.ipynb` | Wear & Lifespan Estimation | XGBoost |
| 5 | `5_XAI_and_Interpretation.ipynb` | Model Transparency & Insights | Permutation Importance |

---

## 📈 Analytical Modules

### 1. Data Foundation (`1_EDA`)
- **Objective:** Validate sensor distribution across 10,000 industrial samples.
- **Key Findings:** Identified 3.5% base failure rate and high correlation between Torque and Rotational Speed.

### 2. Feature Engine (`2_Feature_Engineering`)
- **Interaction Terms:** `Stress Index` (Torque × Wear) and `Thermal Delta` (Process - Air Temp).
- **Anomaly Detection:** Utilizes **Isolation Forest** to flag non-standard operating conditions.
- **Outputs:** Generates `raw` and `scaled` datasets for downstream model consumption.

### 3. Failure Core (`3_Failure_Classification`)
- **Algorithm:** XGBoost Binary Classifier.
- **Optimization:** Stratified 5-Fold Cross-Validation with focus on **Recall** (target > 95%).
- **Artifact:** `xgboost_classifier.pkl` (Joblib).

### 4. Lifespan Prognosis (`4_RUL_Prognosis`)
- **Algorithm:** XGBoost Regressor.
- **Methodology:** Trained on **Raw** features to maintain tree-split consistency.
- **Metric:** Test MAE < 1.0 min (Investment-grade accuracy).
- **Artifact:** `xgboost_wear_regressor.xgb`.

### 5. Transparency Layer (`5_XAI`)
- **Interpretation:** Shifted from SHAP to **Permutation Importance** for localized feature impact analysis.
- **Outcome:** Provides operators with "Reason Codes" for every automated work order.

---

## 🚀 Usage Guide

### Installation
```bash
pip install -r requirements.txt
jupyter notebook
```

### Critical Execution Note
Notebooks must be run in sequential order (1 → 5) as each stage generates artifacts required by the next.

---

**Last Updated:** March 2026  
**Status:** Validated & Hardened
