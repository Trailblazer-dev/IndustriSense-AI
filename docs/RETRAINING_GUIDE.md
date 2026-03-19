# 🔄 IndustriSense AI Retraining Guide (MLOps)

This guide explains how to perform automated model retraining for the IndustriSense AI platform. The system has been transitioned from manual Jupyter Notebooks to professional Python scripts with automated validation and deployment logic.

---

## 🏗️ Retraining Logic (MLOps Workflow)

Every time a retraining script is executed, the system follows these steps:

1.  **Data Loading**: Pulls the latest engineered data from `data/processed/`.
2.  **Model Training**: Trains a new XGBoost model using optimized hyperparameters.
3.  **Performance Evaluation**: Computes metrics (Recall for Classifier, MAE for Regressor) on a held-out test set.
4.  **Automated Validation**: Compares the new model's performance against the **current production model**.
5.  **Artifact Swapping**:
    *   If the new model is **better or equal**, it automatically backs up the old model and deploys the new artifacts to `src/models/`.
    *   If the new model is **worse**, it skips deployment to prevent performance regression.
6.  **Metadata Update**: Updates `model_metadata.json` or `rul_metadata.json` with the new performance scores and timestamps.

---

## 🚀 How to Run Retraining

### 1. Retrain Failure Classifier
Used to improve failure detection and risk probability accuracy.
```bash
./scripts/train_classifier.sh
```

### 2. Retrain RUL Regressor
Used to improve tool wear estimation and remaining useful life accuracy.
```bash
./scripts/train_rul_model.sh
```

---

## 📁 Artifact Locations

*   **Production Models**: `src/models/xgboost_classifier.pkl` and `xgboost_wear_regressor.pkl`.
*   **Backups**: Previous models are stored in `src/models/backups/` with timestamps (e.g., `src/models/backups/20260313_093000/`).
*   **Performance Reports**: Metrics are documented in `model_metadata.json` and `rul_metadata.json`.

---

## 🛠️ When to Retrain?

1.  **Data Drift**: If you notice that real-world sensor values (e.g., higher average factory temperature) are shifting away from the training distribution.
2.  **High Error Margins**: If the "Actual vs Predicted" variance in the Dashboard Transparency Reports is consistently high.
3.  **New Equipment**: After collecting at least 1,000 new samples from a new type of machine.

---

**Status:** ✅ MLOps Automated  
**Maintainer:** Senior ML Engineer
