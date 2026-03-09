Model artifacts and conversion utilities
=====================================

This folder contains trained model artifacts and helper tools to manage model deployment.

Files added:
- `convert_models.py`: script to convert existing pickled XGBoost sklearn wrappers to native `.xgb` booster files and write a `.sha256` checksum next to them.
- `model_utils.py`: runtime helpers to load models safely. Prefers native `.xgb` artifacts and wraps boosters with a minimal sklearn-like interface. Falls back to existing `.pkl` files when needed.

Recommended conversion workflow (developer machine / CI):

1. Create a Python environment and install required packages (including `xgboost`):

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
pip install xgboost
```

2. Run the conversion script to export `.xgb` files:

```bash
python src/models/convert_models.py
```

3. Verify `.xgb` and `.sha256` files were created under `src/models/`.

Notes:
- If `xgboost` is not installed on the host, `model_utils` will still import but native `.xgb` support will be disabled; the app will fall back to loading pickled artifacts where available.
- Converting pickles to `.xgb` is only possible when the pickled object exposes a booster (e.g., XGBClassifier/Regressor sklearn wrappers or xgboost.Booster instances).
