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

## Project Structure

- `data/`: Contains the raw and processed datasets.
- `notebooks/`: Jupyter notebooks for exploration and analysis.
- `src/`: Source code for data processing, feature engineering, modeling, and visualization.
- `scripts/`: Shell scripts for running pipelines.
- `mlops/`: Contains components for Machine Learning Operations (MLOps), including:
    - `ci-cd/`: Continuous Integration and Continuous Deployment (CI/CD) pipelines.
    - `monitoring/`: Data and model drift monitoring.
    - `provenance/`: Provenance management system for data lineage and audit trails.
- `tests/`: Unit tests for the source code.
- `config/`: Configuration files.
- `requirements.txt`: Python dependencies.

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
