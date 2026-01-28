+# IndustriSense-AI: Predictive Maintenance

## Overview

IndustriSense-AI is a **prototype system for batch-mode predictive maintenance analysis** using the AI4I 2020 dataset. It demonstrates core machine learning and XAI capabilities for analyzing sensor data snapshots to assess machinery health and failure risk.

### System Scope (Prototype)

**What this system does:**
- Analyzes cross-sectional sensor data snapshots (e.g., "Given today's readings, assess failure risk")
- Predicts **failure classification** using XGBoost on engineered features (Stress Index, Temperature Differential)
- Generates **SHAP-based explainability** for failure predictions
- Estimates **component wear (RUL proxy)** analytically from sensor features

**What this system does NOT do (requires architectural changes):**
- ~~Real-time continuous monitoring~~ (Requires streaming data architecture)
- ~~Temporal trend analysis~~ (Requires time-series data collection with machine IDs and timestamps)
- ~~CLSTM-based RUL prognosis~~ (Requires longitudinal degradation profiles per machine)

## Two Core Pipelines

1.  **Failure Classification:** Predicts the probability of imminent machine failure (binary: Machine failure = 0/1) and specific failure modes (TWF, HDF, PWF, OSF, RNF).
2.  **Component Wear Analysis:** Estimates remaining tool wear/lifespan (RUL proxy) based on current sensor readings and operational features.

The project follows the methodology outlined in the supporting domain documents ("AI Predictive Maintenance Project Steps.pdf" and "Predictive Maintenance for KTDA...pdf").

---

## 🚀 Installation & Setup Guide

### Prerequisites
- **Python** 3.8 or higher
- **pip** package manager
- **Git** (for cloning the repository)

### Step 1: Clone the Repository
```bash
git clone https://github.com/Trailblazer-dev/IndustriSense-AI.git
cd IndustriSense-AI
```

### Step 2: Create a Virtual Environment (Recommended)

**On Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Jupyter (if not already included)
```bash
pip install jupyter notebook
```

### Step 5: Verify Installation
```bash
python --version
pip list
```

### Step 6: Launch Jupyter Notebook
```bash
jupyter notebook
```

Navigate to the `notebooks/` folder and start with:
1. **1_EDA.ipynb** - Exploratory Data Analysis
2. **2_Feature_Engineering.ipynb** - Feature Engineering
3. **3_Failure_Classification_Modeling.ipynb** - Classification Model
4. **4_RUL_Prognosis_Modeling.ipynb** - RUL Estimation
5. **5_XAI_and_Interpretation.ipynb** - Explainability Analysis

---

### Quick Start Example

```python
# After installing dependencies and launching Jupyter
import pandas as pd
from src.data.make_dataset import load_data
from src.models.predict import predict_failure

# Load data
X, y = load_data()

# Make predictions
predictions = predict_failure(X)
print(predictions)
```

### Configuration

Key configuration files:
- `requirements.txt` - Python package dependencies
- `data/` - Raw and processed datasets
- `src/` - Source code modules

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_models.py
```

### Running Training Scripts

```bash
# Train classifier model
bash scripts/train_classifier.sh

# Train RUL model
bash scripts/train_rul_model.sh

# Run predictions
bash scripts/run_prediction.sh
```

---

## Project Structure

```
IndustriSense-AI/
├── README.md                          # Main project documentation
├── requirements.txt                   # Python dependencies
│
├── docs/                              # 📚 Organized Documentation
│   ├── DOCUMENTATION_INDEX.md         # Complete documentation index
│   ├── project/                       # Project specs and design
│   │   ├── SRS.md
│   │   ├── FEASIBILITY_SUMMARY.md
│   │   ├── MANIFEST.md
│   │   └── DELIVERY_SUMMARY.txt
│   ├── notebooks/                     # Notebook-specific docs
│   │   ├── NOTEBOOK_README.md
│   │   ├── NOTEBOOK_ARCHITECTURE_GUIDE.md
│   │   ├── NOTEBOOK_DESIGN_DELIVERABLES.md
│   │   ├── TRAIN_TEST_SPLIT_IMPLEMENTATION.md
│   │   └── [other notebook docs]
│   └── audit/                         # Audit documentation
│       ├── AUDIT_REPORT.md
│       ├── AUDIT_CHECKLIST.md
│       └── [other audit docs]
│
├── data/                              # 📊 Data Directory
│   ├── raw/                           # Original datasets
│   │   ├── ai4i2020.csv
│   │   └── predictive_maintenance.csv
│   └── processed/                     # Processed datasets
│       ├── features_engineered_raw.csv
│       └── features_engineered_scaled.csv
│
├── notebooks/                         # 📓 Jupyter Notebooks
│   ├── 1_EDA.ipynb                    # Exploratory Data Analysis
│   ├── 2_Feature_Engineering.ipynb    # Feature Engineering
│   ├── 3_Failure_Classification_Modeling.ipynb
│   ├── 4_RUL_Prognosis_Modeling.ipynb
│   └── 5_XAI_and_Interpretation.ipynb # Explainability Analysis
│
├── src/                               # 🔧 Source Code
│   ├── data/
│   │   ├── __init__.py
│   │   └── make_dataset.py            # Data loading & preprocessing
│   ├── features/
│   │   ├── __init__.py
│   │   └── build_features.py          # Feature engineering
│   ├── models/
│   │   ├── __init__.py
│   │   ├── classification_model.py    # Failure classification
│   │   ├── rul_model.py               # RUL estimation
│   │   └── predict.py                 # Prediction utilities
│   └── visualization/
│       ├── __init__.py
│       └── visualize.py               # Visualization utilities
│
├── scripts/                           # 🔨 Automation Scripts
│   ├── train_classifier.sh            # Train classifier model
│   ├── train_rul_model.sh             # Train RUL model
│   └── run_prediction.sh              # Run predictions
│
├── tests/                             # ✅ Unit Tests
│   ├── test_data.py
│   ├── test_features.py
│   └── test_models.py
│
├── mlops/                             # (Optional MLOps structure)
│   ├── ci-cd/                         # CI/CD pipelines
│   ├── monitoring/                    # Model monitoring
│   └── provenance/                    # Data lineage tracking
│
└── [Reference Documents]
    ├── AI Predictive Maintenance Project Steps.pdf
    └── Predictive Maintenance for KTDA....pdf
```

### Directory Descriptions

- **`data/`**: Contains the raw and processed datasets.
- **`notebooks/`**: Jupyter notebooks for exploration and analysis.
- **`src/`**: Source code for data processing, feature engineering, modeling, and visualization.
- **`scripts/`**: Shell scripts for running pipelines.
- **`tests/`**: Unit tests for the source code.
- **`docs/`**: Complete project documentation organized by category (see [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md))
- **`mlops/`**: Components for Machine Learning Operations (MLOps), including CI/CD pipelines, monitoring, and data provenance.



## Critical System Limitations

### Dataset Constraint
The AI4I 2020 dataset is a **static snapshot** (10,000 observations, no timestamps or machine identifiers). This imposes fundamental limits:

| Capability | Status | Reason |
|-----------|--------|--------|
| **Failure Classification** | ✓ FEASIBLE | Cross-sectional XGBoost classification on sensor features |
| **Component Wear Estimation** | ✓ FEASIBLE | Tool Wear (0-254 min) used as RUL proxy from snapshot data |
| **Stress Index Feature** | ✓ FEASIBLE | EDA confirms feature discriminates overstrain failures (OSF mean: 12,067 vs. 4,238) |
| **Temperature Differential** | ✓ FEASIBLE | EDA-validated feature for heat dissipation failures (HDF) |
| **Real-Time Monitoring** | ✗ NOT FEASIBLE | Requires streaming data + persistent storage of time-series per machine |
| **Thermal Trend Calculation** | ✗ NOT FEASIBLE | Requires time-indexed temperature sequences per machine |
| **CLSTM RUL Prognosis** | ✗ NOT FEASIBLE | Requires longitudinal degradation profiles showing component wear over time |
| **Financial Impact Tracker** | ✗ NOT FEASIBLE | Dataset lacks downtime logs, maintenance costs, and revenue data |

### Design Implications
- System operates in **batch mode**: "Given a snapshot of sensor readings, predict failure risk"
- Not suitable for continuous state tracking or temporal trend detection
- RUL output is analytical (component wear estimate) not predictive (future degradation trajectory)

---

## 📚 Documentation

All project documentation has been organized in the `docs/` folder for easy navigation:

| Category | Location | Purpose |
|----------|----------|---------|
| **Project Specs** | [docs/project/](docs/project/) | SRS, feasibility analysis, requirements |
| **Notebook Docs** | [docs/notebooks/](docs/notebooks/) | Architecture, standards, best practices |
| **Audit Reports** | [docs/audit/](docs/audit/) | Audit trails, compliance, validation |

**Start here:** [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) - Complete documentation index with links to all resources.

---

## 🤝 Contributing

To contribute to this project:

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all tests pass: `python -m pytest tests/`
4. Submit a pull request

## 📝 License

This project is provided as-is for educational and research purposes.

## 📧 Contact & Support

For questions or issues, please refer to the project documentation or open an issue on GitHub.

---

**Last Updated:** January 2026
