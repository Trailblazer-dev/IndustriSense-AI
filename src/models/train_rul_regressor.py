"""Train RUL regressor (XGBoost) with MLOps best practices.

This script:
- Loads `data/processed/features_engineered_raw.csv`
- Trains an `xgboost.XGBRegressor` using 80/20 split
- Evaluates on a hold-out test set
- Compares performance with the existing production model (MAE comparison)
- Automatically swaps artifacts if the new model is superior
- Maintains model metadata and integrity hashes

Run:
    python -m src.models.train_rul_regressor
"""
import os
import json
import joblib
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import xgboost as xgb

RANDOM_STATE = 42
MODEL_NAME = "xgboost_wear_regressor"
PRIMARY_METRIC = "mae"  # Lower is better

def sha256_file(path: Path) -> str:
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def get_existing_performance(model_dir: Path) -> Optional[float]:
    """Extract primary metric (MAE) from existing metadata."""
    metadata_path = model_dir / "rul_metadata.json"
    if not metadata_path.exists():
        return None
    try:
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
            perf = meta.get('test_performance', {}).get(PRIMARY_METRIC)
            return float(perf) if perf is not None else None
    except Exception:
        return None

def main():
    repo_root = Path(__file__).resolve().parents[2]
    data_path = repo_root / 'data' / 'processed' / 'features_engineered_raw.csv'
    model_dir = repo_root / 'src' / 'models'
    temp_dir = model_dir / 'temp_train_rul'
    temp_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    features = [
        'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
        'Torque [Nm]', 'Temp Diff [K]', 'Speed_x_Torque', 'is_anomaly'
    ]
    target_col = 'Tool wear [min]'

    # Sanitize feature names for XGBoost
    def sanitize(name: str) -> str:
        import re
        s = re.sub(r"[^0-9a-zA-Z_]", "_", name)
        s = re.sub(r"__+", "_", s)
        if s[0].isdigit():
            s = "f_" + s
        return s

    feature_name_map = {orig: sanitize(orig) for orig in features}

    X = df[features].copy()
    y = df[target_col].astype(float).copy()
    X_renamed = X.rename(columns=feature_name_map)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_renamed, y, test_size=0.2, random_state=RANDOM_STATE
    )

    params = {
        'objective': 'reg:squarederror',
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': RANDOM_STATE
    }

    print("Training new RUL regressor...")
    model = xgb.XGBRegressor(**params)
    model.fit(X_train, y_train)

    # Evaluation
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2 = r2_score(y_test, y_pred)

    metrics = {
        'mae': float(mae),
        'rmse': float(rmse),
        'r2': float(r2),
        'test_samples': int(len(y_test))
    }

    print("New model metrics:", json.dumps(metrics, indent=2))

    # Validation logic
    existing_perf = get_existing_performance(model_dir)
    new_perf = metrics[PRIMARY_METRIC]

    should_deploy = False
    if existing_perf is None:
        print("No existing model found. Deploying new model as baseline.")
        should_deploy = True
    elif new_perf <= existing_perf:  # MAE: lower is better
        print(f"New model improves {PRIMARY_METRIC} ({new_perf:.4f} <= {existing_perf:.4f}).")
        should_deploy = True
    else:
        print(f"New model did not outperform existing model ({new_perf:.4f} > {existing_perf:.4f}).")
        print("Deployment skipped.")

    if should_deploy:
        # Save to temp paths
        new_joblib = temp_dir / f"{MODEL_NAME}.joblib"
        new_xgb = temp_dir / f"{MODEL_NAME}.xgb"
        
        joblib.dump(model, new_joblib)
        model.get_booster().save_model(str(new_xgb))
        
        new_sha = sha256_file(new_xgb)
        with open(temp_dir / f"{MODEL_NAME}.xgb.sha256", 'w') as f:
            f.write(new_sha)

        # Atomic Swap / Backup
        prod_joblib = model_dir / f"{MODEL_NAME}.joblib"
        prod_xgb = model_dir / f"{MODEL_NAME}.xgb"
        prod_sha = model_dir / f"{MODEL_NAME}.xgb.sha256"
        prod_meta = model_dir / "rul_metadata.json"

        backup_dir = model_dir / 'backups' / f"rul_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"Backing up current artifacts to {backup_dir}...")
        for p in [prod_joblib, prod_xgb, prod_sha, prod_meta]:
            if p.exists():
                shutil.copy(p, backup_dir / p.name)

        print("Swapping artifacts to production...")
        if new_joblib.exists():
            shutil.move(str(new_joblib), str(prod_joblib))
        shutil.move(str(new_xgb), str(prod_xgb))
        shutil.move(str(temp_dir / f"{MODEL_NAME}.xgb.sha256"), str(prod_sha))

        # Update metadata
        metadata = {
            'model_type': 'XGBoost Wear Regressor (RUL Proxy)',
            'last_trained': datetime.now().isoformat(),
            'hyperparameters': params,
            'test_performance': metrics,
            'features': features,
            'feature_name_map': feature_name_map,
            'sha256': new_sha,
            'rul_conversion': 'RUL = 254 - Predicted_Wear (minutes)'
        }
        with open(prod_meta, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Model successfully deployed.")

    # Cleanup temp
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
