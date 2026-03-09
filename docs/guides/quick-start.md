# 🚀 Quick Start Guide

Get up and running with IndustriSense-AI in **3 simple steps**.

---

## Step 1️⃣: Environment Setup

```bash
# Clone repository
git clone https://github.com/Trailblazer-dev/IndustriSense-AI.git
cd IndustriSense-AI

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
# or
source venv/bin/activate          # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

**Detailed setup guide:** See [../README.md](../README.md#-installation--setup-guide) for complete instructions.

---

## Step 2️⃣: Understand the Project

| Aspect | Resource |
|--------|----------|
| **What it does** | [../README.md](../README.md#overview) |
| **System limitations** | [../README.md](../README.md#critical-system-limitations) |
| **Core pipelines** | [../README.md](../README.md#two-core-pipelines) |
| **All documentation** | [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) |

---

## Step 3️⃣: Explore the Code

### Launch Jupyter
```bash
jupyter notebook
```

### Run Notebooks in Order

1. **[1_EDA.ipynb](../../notebooks/1_EDA.ipynb)** ← **START HERE**
   - Exploratory data analysis
   - Dataset overview (10,000 samples, 16 features)
   - Feature distributions and correlations

2. **[2_Feature_Engineering.ipynb](../../notebooks/2_Feature_Engineering.ipynb)**
   - Create engineered features (Stress Index, Thermal Differential)
   - Anomaly detection using Isolation Forest
   - Generate raw and scaled datasets

3. **[3_Failure_Classification_Modeling.ipynb](../../notebooks/3_Failure_Classification_Modeling.ipynb)**
   - Train XGBoost classifier
   - Predict failure probability
   - Feature importance analysis

4. **[4_RUL_Prognosis_Modeling.ipynb](../../notebooks/4_RUL_Prognosis_Modeling.ipynb)**
   - Train XGBoost regressor
   - Estimate tool wear/remaining useful life
   - Cross-validation and testing

5. **[5_XAI_and_Interpretation.ipynb](../../notebooks/5_XAI_and_Interpretation.ipynb)**
   - SHAP explainability analysis
   - Understand model decisions
   - Interpretation guides for operators

---

## Common Commands

```bash
# Run tests
python -m pytest tests/

# Train classification model
bash scripts/train_classifier.sh

# Train RUL/regression model
bash scripts/train_rul_model.sh

# Run batch predictions
bash scripts/run_prediction.sh

# Start web app
cd web_app && python app.py
```

---

## Project Structure

```
IndustriSense-AI/
│
├── README.md                    ← Project overview & setup
├── requirements.txt             ← Python dependencies
│
├── notebooks/                   ← Jupyter notebooks (5 total)
│   ├── 1_EDA.ipynb             ← Start here!
│   ├── 2_Feature_Engineering.ipynb
│   ├── 3_Failure_Classification_Modeling.ipynb
│   ├── 4_RUL_Prognosis_Modeling.ipynb
│   └── 5_XAI_and_Interpretation.ipynb
│
├── src/                         ← Python source code
│   ├── data/                   ← Data loading & processing
│   ├── features/               ← Feature engineering
│   ├── models/                 ← Model training & inference
│   └── visualization/          ← Plotting utilities
│
├── data/                        ← Datasets
│   └── processed/              ← Engineered features (raw & scaled)
│
├── web_app/                     ← Flask web application
│   └── Run with: python app.py
│
├── scripts/                     ← Automation scripts
│
├── tests/                       ← Unit tests
│
└── docs/                        ← Complete documentation
    ├── guides/                 ← Setup & usage guides
    ├── architecture/           ← System design & ML pipeline
    ├── deployment/             ← Web app & troubleshooting
    ├── audit/                  ← Compliance & reports
    ├── notebooks/              ← Notebook standards & patterns
    └── project/                ← Requirements & specifications
```

---

## Next Steps

### 👨‍💻 For Developers
- [Notebook Architecture Guide](../notebooks/architecture.md) - Design patterns and structure
- [ML Pipeline Troubleshooting](../deployment/ml-troubleshooting.md) - Common issues & fixes
- [API Reference](../deployment/web-app.md) - Web app endpoints

### 🚀 For Deployment
- [Web App Documentation](../deployment/web-app.md) - Running the Flask dashboard
- [Verification Checklist](../deployment/verification.md) - Testing procedures
- [ML Troubleshooting](../deployment/ml-troubleshooting.md) - Debugging guide

### 📚 For Full Details
- [Complete Documentation Index](../DOCUMENTATION_INDEX.md)
- [System Requirements Specification](../project/SRS.md)

---

## What Is IndustriSense-AI?

✅ **What it does:**
- Predict machinery failures using XGBoost
- Estimate component wear and remaining lifespan
- Explain predictions using SHAP
- Analyze sensor data snapshots (batch mode)

❌ **What it doesn't do:**
- Real-time monitoring (needs streaming architecture)
- Temporal trend analysis (needs historical time-series)
- Time-series forecasting (dataset limitation)

**Read more:** [../README.md](../README.md)

---

## Quick Code Example

```python
import pandas as pd
from src.data.make_dataset import load_data
from src.models.predict import predict_failure, predict_wear
import pickle

# Load data
X, y_classifier, y_regressor = load_data()

# Load trained models
with open('src/models/xgboost_classifier.pkl', 'rb') as f:
    classifier = pickle.load(f)
    
with open('src/models/xgboost_wear_regressor.pkl', 'rb') as f:
    regressor = pickle.load(f)

# Make predictions
failure_prob = classifier.predict_proba(X)[:, 1]
wear_pred = regressor.predict(X)
rul_pred = 253 - wear_pred  # Calculate RUL

print(f"Failure Probability: {failure_prob[0]:.1%}")
print(f"Estimated Wear: {wear_pred[0]:.1f} min")
print(f"Remaining Useful Life: {rul_pred[0]:.1f} min")
```

---

## 🆘 Need Help?

| Question | Resource |
|----------|----------|
| Something's broken | [../deployment/ml-troubleshooting.md](../deployment/ml-troubleshooting.md) |
| How do I run the web app? | [../deployment/web-app.md](../deployment/web-app.md) |
| Model isn't predicting correctly | [../deployment/verification.md](../deployment/verification.md) |
| Need technical details? | [../architecture/ml-pipeline.md](../architecture/ml-pipeline.md) |
| Can't find something? | [../DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) |

---

**Happy exploring! 🎉**
