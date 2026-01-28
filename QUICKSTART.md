# 🚀 Quick Start Guide

## First Time Here? Start with These 3 Steps

### 1️⃣ **Setup Your Environment**
```bash
# Clone the repository
git clone https://github.com/Trailblazer-dev/IndustriSense-AI.git
cd IndustriSense-AI

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

**Full setup guide:** [README.md](README.md#-installation--setup-guide)

### 2️⃣ **Understand the Project**
- **Overview:** [README.md](README.md#overview)
- **How it works:** [README.md](README.md#two-core-pipelines)
- **What it can/cannot do:** [README.md](README.md#critical-system-limitations)

### 3️⃣ **Explore the Code**
Launch Jupyter and work through notebooks in order:

```bash
jupyter notebook
```

Then open and run:
1. **[1_EDA.ipynb](notebooks/1_EDA.ipynb)** - Data exploration (start here!)
2. **[2_Feature_Engineering.ipynb](notebooks/2_Feature_Engineering.ipynb)** - Feature creation
3. **[3_Failure_Classification_Modeling.ipynb](notebooks/3_Failure_Classification_Modeling.ipynb)** - Model training
4. **[4_RUL_Prognosis_Modeling.ipynb](notebooks/4_RUL_Prognosis_Modeling.ipynb)** - RUL estimation
5. **[5_XAI_and_Interpretation.ipynb](notebooks/5_XAI_and_Interpretation.ipynb)** - Understanding results

---

## 📚 Need Documentation?

| I need... | Go to... |
|-----------|----------|
| **Installation help** | [README.md - Setup Guide](README.md#-installation--setup-guide) |
| **Project overview** | [README.md](README.md) |
| **System requirements** | [docs/project/SRS.md](docs/project/SRS.md) |
| **All documentation** | [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) |
| **Navigation map** | [PROJECT_STRUCTURE_MAP.md](PROJECT_STRUCTURE_MAP.md) |
| **Notebook guidelines** | [docs/notebooks/NOTEBOOK_README.md](docs/notebooks/NOTEBOOK_README.md) |
| **Troubleshooting** | [docs/ORGANIZATION_SUMMARY.md](docs/ORGANIZATION_SUMMARY.md) |

---

## 💡 What is IndustriSense-AI?

**Predictive Maintenance System** that:
- ✅ Predicts machinery failures using XGBoost
- ✅ Estimates component wear/remaining lifespan
- ✅ Explains predictions using SHAP
- ✅ Works with sensor data snapshots (batch mode)

**Not suitable for:**
- ❌ Real-time monitoring (requires streaming)
- ❌ Temporal trend analysis (requires historical data)
- ❌ Time-series forecasting (dataset limitation)

---

## 🛠️ Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run Jupyter
jupyter notebook

# Run tests
python -m pytest tests/

# Train classification model
bash scripts/train_classifier.sh

# Train RUL model
bash scripts/train_rul_model.sh

# Run predictions
bash scripts/run_prediction.sh
```

---

## 📊 Project Structure

```
├── README.md              ← Project overview & setup
├── notebooks/             ← Jupyter notebooks (start with 1_EDA.ipynb)
├── src/                   ← Python source code
├── data/                  ← Datasets
├── scripts/               ← Automation scripts
├── tests/                 ← Unit tests
└── docs/                  ← Organized documentation
    ├── project/           ← Requirements & specs
    ├── notebooks/         ← Best practices & guides
    └── audit/             ← Compliance & reports
```

**Full structure diagram:** [PROJECT_STRUCTURE_MAP.md](PROJECT_STRUCTURE_MAP.md)

---

## ⚡ Quick Code Example

```python
import pandas as pd
from src.data.make_dataset import load_data
from src.models.predict import predict_failure

# Load data
X, y = load_data()

# Make predictions
predictions = predict_failure(X)

# View results
print(f"Failure probability: {predictions['failure_prob']}")
print(f"Predicted failures: {predictions['failure_count']}")
```

---

## ❓ Stuck?

1. Check the full [README.md](README.md) for detailed setup
2. Browse [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) for all docs
3. See [PROJECT_STRUCTURE_MAP.md](PROJECT_STRUCTURE_MAP.md) for navigation
4. Review relevant notebook documentation in `docs/notebooks/`

---

## 📝 Contributing

1. Create a feature branch
2. Make changes
3. Run tests: `python -m pytest tests/`
4. Submit pull request

See [README.md - Contributing](README.md#-contributing) for details.

---

**Ready? Start with step 1 above! 🚀**

*Last updated: January 2026*
