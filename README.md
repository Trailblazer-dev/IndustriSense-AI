# IndustriSense-AI: Predictive Maintenance

This project implements a predictive maintenance solution for industrial machinery using the AI4I 2020 dataset. It includes two main pipelines:
1.  **Failure Classification:** Predicts imminent machine failures.
2.  **RUL Prognosis:** Estimates the Remaining Useful Life of machinery.

The project follows the methodology outlined in the "AI Predictive Maintenance Project Steps.pdf" document.

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
