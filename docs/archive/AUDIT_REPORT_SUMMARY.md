Audit Summary — Predictive Maintenance Project

Date: 2026-03-05

Scope: technical audit of RUL/regression pipeline, model artifacts, web app, and repo hygiene.

Top (Priority) Findings & Actions Taken

1) Secrets & debug flags in repo (High)
- Finding: `.env`/`.env.example` contained placeholder secrets and `DEBUG=True` in examples.
- Action: Removed hard-coded secrets from examples; added guidance to rotate any exposed credentials.
- Next: Use a secret manager for production (Azure KeyVault / AWS Secrets Manager / env injection).

2) Unsafe model deserialization (High)
- Finding: Models were loaded via unverified pickles at import-time.
- Action: Added `src/models/model_utils.py` to prefer native XGBoost `.xgb` artifacts and compute SHA256 checksums. Added `src/models/convert_models.py` to export `.xgb` where possible.
- Next: Replace remaining pickle-only artifacts with `.xgb` and enforce checksum verification in CI.

3) Data leakage in RUL regressor (High)
- Finding: Interaction features leaked label information (noted during EDA); earlier notebook claimed near-perfect CV R².
- Action: Added `src/models/train_rul_regressor.py` that removes leaky features and retrains reproducibly. Retrained model saved to `src/models/`.
- Result: Realistic (non-leaky) test performance: MAE=51.31 min, RMSE=61.86 min, R²=0.1036 on 2,000 held-out samples.
- Next: Re-evaluate feature engineering; add temporal data in Phase 2 for true RUL prognosis.

4) App startup & safety (Medium)
- Finding: Models loaded at module import; lack of input validation and global CORS.
- Action: Refactored `web_app/app.py` to lazy-load models, added input validation, centralized `MAX_TOOL_WEAR` in `web_app/config.py`, and limited CORS via `ALLOWED_ORIGINS`.
- Next: Add health-check endpoints, signed artifact verification, and production WSGI config (Gunicorn/uvicorn).

5) Reproducibility and artifacts (Medium)
- Action: Training script writes `.pkl`, `.xgb`, `.xgb.sha256`, `rul_metadata.json`, and CSV metrics to `src/models/`.
- Repro command: `python -m src.models.train_rul_regressor` (ensure environment from `requirements.txt`).

6) Tests & CI (Medium)
- Finding: Repository contains unit tests (`tests/`) but test run failed in current environment due to missing packages (`pytest`, `pandas`).
- Action: None automated yet (manual dependency install required).
- Next: Run locally or in CI after installing dependencies: `python -m pip install -r requirements.txt` then `python -m pytest -q`.

Artifacts & Locations
- Trained regressor: `src/models/xgboost_wear_regressor.pkl` and `src/models/xgboost_wear_regressor.xgb`
- Checksum: `src/models/xgboost_wear_regressor.xgb.sha256`
- Metadata: `src/models/rul_metadata.json`
- CV & test metrics: `src/models/rul_cv_results.csv`, `src/models/rul_test_results.csv`
- Feature importance: `src/models/wear_feature_importance.csv`

Immediate Next Steps (recommended)
1. Install dependencies and run full test suite locally or via CI:

   python -m pip install -r requirements.txt
   python -m pytest -q

2. Replace all remaining pickle-only artifacts with `.xgb` and enable checksum verification in the app and CI.
3. Add a model registry or storage (e.g., Azure Blob + metadata + signed checksums) and CI validation on artifact uploads.
4. Add unit/integration tests for `web_app` endpoints (smoke tests) and an automated notebook execution check for critical notebooks.
5. Review feature-engineering pipeline and consider Phase 2 data collection for true temporal RUL models.

If you want, I can:
- Run the dependency install and tests here (requires network & time),
- Create a Git commit for the changes and open a PR, or
- Implement CI (GitHub Actions) to run tests + artifact checksum verification.

Concise status (todos):
- Most audit remediation tasks implemented (model safety, retrain, app hardening, notebook updates).
- Remaining manual steps: install deps & run tests; optionally add CI and registry work.
