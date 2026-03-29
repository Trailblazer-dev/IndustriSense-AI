# 🚀 Quick Start Guide

Get up and running with IndustriSense AI in **3 simple steps**.

---

## Step 1️⃣: Environment Setup

### Local Development
```bash
# Clone repository
git clone https://github.com/Trailblazer-dev/IndustriSense-AI.git
cd IndustriSense-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Docker (Recommended)
```bash
docker compose up --build -d
```

---

## Step 2️⃣: Understand the Project

| Aspect | Resource |
|--------|----------|
| **Architecture** | [../project/SDD.md](../project/SDD.md) |
| **Requirements** | [../project/SRS.md](../project/SRS.md) |
| **Subscription Tiers** | [../README.md](../README.md#user-roles--multi-tenancy) |
| **All Documentation** | [../README.md](../README.md) |

---

## Step 3️⃣: Explore the Pipeline

### Running Notebooks
```bash
jupyter notebook
```

**Order of execution:**
1. `1_EDA.ipynb`: Initial data exploration.
2. `2_Feature_Engineering.ipynb`: Interaction generation & scaling.
3. `3_Failure_Classification_Modeling.ipynb`: Classifier training (XGBoost).
4. `4_RUL_Prognosis_Modeling.ipynb`: Regressor training (XGBoost).
5. `5_XAI_and_Interpretation.ipynb`: Permutation importance & interpretation.

---

## Common Commands

```bash
# Run web application (Local)
cd web_app && python run.py

# Run unit tests
python -m unittest discover tests/

# Execute background tasks (Worker)
celery -A web_app.app.tasks:celery worker --loglevel=info
```

---

## Project Structure

```
IndustriSense-AI/
│
├── README.md                    ← Project overview & setup
├── requirements.txt             ← Global dependencies
│
├── notebooks/                   ← Data Science pipeline
│
├── src/                         ← Core logic
│   └── models/                 ← Model utilities & artifacts
│
├── data/                        ← Training & processed data
│
├── web_app/                     ← Flask application
│   ├── app/                    ← Modular blueprint logic
│   ├── static/                 ← CSS/JS assets
│   └── templates/              ← Jinja2 views
│
├── scripts/                     ← Database & setup automation
│
└── docs/                        ← Technical documentation
```

---

## What Is IndustriSense AI?

✅ **What it does:**
- Predict machinery failures using dual-core XGBoost.
- Estimate Remaining Useful Life (RUL) via tool-wear proxies.
- Explain predictions using Permutation Importance.
- Multi-tenant data isolation for industrial facilities.

❌ **What it doesn't do:**
- Temporal trend analysis (Cross-sectional data limitation).
- Real-time PLC hardware control (Monitoring only).

---

**Happy exploring! 🎉**
