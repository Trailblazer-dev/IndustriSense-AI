"""Train RUL regressor (XGBoost) using clean sensor-only features.

This script:
- Loads `data/processed/features_engineered_raw.csv` (training distribution)
- Removes leaky features derived from the target (`Stress Index`, `Temp_Diff_x_Wear`)
- Trains an `xgboost.XGBRegressor` with fixed random seed for reproducibility
- Evaluates on a hold-out test set and writes metrics to `src/models/rul_test_results.csv`
- Saves artifacts: `xgboost_wear_regressor.pkl` (pickle of sklearn estimator) and
  `xgboost_wear_regressor.xgb` (native booster), plus `xgboost_wear_regressor.xgb.sha256`.

Run:
    python -m src.models.train_rul_regressor
"""
import os
import json
import pickle
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import xgboost as xgb


RANDOM_STATE = 42


def main():
    repo_root = Path(__file__).resolve().parents[2]
    data_path = repo_root / 'data' / 'processed' / 'features_engineered_raw.csv'
    model_dir = repo_root / 'src' / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    df = pd.read_csv(data_path)

    # Target and feature selection
    target_col = 'Tool wear [min]'

    # Remove leaky features derived from the target
    leaky = ['Stress Index', 'Temp_Diff_x_Wear']
    features: List[str] = [
        'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
        'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly'
    ]

    # Sanitize feature names for XGBoost (no brackets or special chars)
    def sanitize(name: str) -> str:
        import re
        s = re.sub(r"[^0-9a-zA-Z_]", "_", name)
        s = re.sub(r"__+", "_", s)
        if s[0].isdigit():
            s = "f_" + s
        return s

    feature_name_map = {orig: sanitize(orig) for orig in features}
    # Also map target if needed
    target_name_safe = sanitize(target_col)


    missing = [c for c in features + [target_col] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns in data: {missing}")

    X = df[features].copy()
    y = df[target_col].astype(float).copy()

    # Rename columns to safe names before training XGBoost
    X_renamed = X.rename(columns=feature_name_map)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_renamed, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # Model hyperparameters (kept consistent with previous experiments)
    params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': RANDOM_STATE
    }

    model = xgb.XGBRegressor(**params)
    model.fit(X_train, y_train)

    # Predictions and evaluation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    # Some scikit-learn versions don't support the `squared` kwarg.
    # Compute RMSE as sqrt(MSE) for maximum compatibility.
    mse = mean_squared_error(y_test, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_test, y_pred)

    results = {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'test_set_size': int(len(y_test))
    }

    # Save sklearn wrapper as pickle (for backwards compatibility)
    pkl_path = model_dir / 'xgboost_wear_regressor.pkl'
    with open(pkl_path, 'wb') as f:
        pickle.dump(model, f)

    # Save native booster
    xgb_path = model_dir / 'xgboost_wear_regressor.xgb'
    model.get_booster().save_model(str(xgb_path))

    # Compute sha256 of xgb file
    import hashlib

    def sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, 'rb') as fh:
            for chunk in iter(lambda: fh.read(4096), b''):
                h.update(chunk)
        return h.hexdigest()

    sha = sha256_file(xgb_path)
    sha_path = model_dir / (xgb_path.name + '.sha256')
    with open(sha_path, 'w') as f:
        f.write(sha)

    # Write test results CSV
    results_df = pd.DataFrame([{**results}])
    results_df.to_csv(model_dir / 'rul_test_results.csv', index=False)

    # Update rul_metadata.json (include feature name mapping)
    metadata_path = model_dir / 'rul_metadata.json'
    metadata = {
        'model_type': 'XGBoost Wear Regressor (RUL Proxy)',
        'training_approach': '80/20 holdout split',
        'max_tool_wear_minutes': 254,
        'hyperparameters': params,
        'test_performance': results,
        'features_original': features,
        'feature_name_map': feature_name_map,
        'target_original': target_col,
        'target_safe': target_name_safe,
        'rul_conversion': 'RUL = 254 - Predicted_Wear (minutes)'
    }
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print('Training complete. Results:')
    print(json.dumps(results, indent=2))
    print('Saved:', pkl_path, xgb_path, sha_path, metadata_path)


if __name__ == '__main__':
    main()
