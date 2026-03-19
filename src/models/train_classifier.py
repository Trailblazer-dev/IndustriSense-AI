"""Train Failure Classifier (XGBoost) with MLOps best practices.

This script:
- Loads `data/processed/features_engineered_scaled.csv`
- Trains an `xgboost.XGBClassifier` using stratified 80/20 split
- Evaluates on a hold-out test set
- Compares performance with the existing production model
- Automatically swaps artifacts if the new model is superior
- Maintains model metadata and integrity hashes

Run:
    python -m src.models.train_classifier
"""
import os
import json
import pickle
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score, precision_score, f1_score, roc_auc_score

import xgboost as xgb

RANDOM_STATE = 42
MODEL_NAME = "xgboost_classifier"
PRIMARY_METRIC = "recall"  # We prioritize catching failures

def sha256_file(path: Path) -> str:
    """Compute sha256 of a file."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()

def get_existing_performance(model_dir: Path) -> Optional[float]:
    """Extract primary metric from existing metadata."""
    metadata_path = model_dir / "model_metadata.json"
    if not metadata_path.exists():
        return None
    try:
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
            # Check test_performance then cv_performance fallback
            perf = meta.get('test_performance', {}).get(PRIMARY_METRIC)
            if perf is None:
                perf = meta.get('cv_performance', {}).get(f'mean_{PRIMARY_METRIC}')
            return float(perf) if perf is not None else None
    except Exception:
        return None

def main():
    repo_root = Path(__file__).resolve().parents[2]
    data_path = repo_root / 'data' / 'processed' / 'features_engineered_scaled.csv'
    model_dir = repo_root / 'src' / 'models'
    temp_dir = model_dir / 'temp_train'
    temp_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)

    feature_cols = [
        'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
        'Torque [Nm]', 'Tool wear [min]', 'Stress Index', 'Temp Diff [K]',
        'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
    ]
    target_col = 'Machine failure'

    X = df[feature_cols].values
    y = df[target_col].values

    # Stratified 80/20 split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE, shuffle=True
    )

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
    print(f"Calculated scale_pos_weight: {scale_pos_weight:.2f}")

    params = {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 200,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'scale_pos_weight': scale_pos_weight,
        'random_state': RANDOM_STATE,
        'use_label_encoder': False,
        'eval_metric': 'logloss'
    }

    print("Training new model...")
    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)

    # Evaluation
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        'recall': float(recall_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred)),
        'f1': float(f1_score(y_test, y_pred)),
        'roc_auc': float(roc_auc_score(y_test, y_proba)),
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
    elif new_perf >= existing_perf:
        print(f"New model improves {PRIMARY_METRIC} ({new_perf:.4f} >= {existing_perf:.4f}).")
        should_deploy = True
    else:
        print(f"New model did not outperform existing model ({new_perf:.4f} < {existing_perf:.4f}).")
        print("Deployment skipped.")

    if should_deploy:
        # Save to temp paths
        new_pkl = temp_dir / f"{MODEL_NAME}.pkl"
        new_xgb = temp_dir / f"{MODEL_NAME}.xgb"
        
        with open(new_pkl, 'wb') as f:
            pickle.dump(model, f)
        model.get_booster().save_model(str(new_xgb))
        
        new_sha = sha256_file(new_xgb)
        with open(temp_dir / f"{MODEL_NAME}.xgb.sha256", 'w') as f:
            f.write(new_sha)

        # Atomic Swap / Backup
        prod_pkl = model_dir / f"{MODEL_NAME}.pkl"
        prod_xgb = model_dir / f"{MODEL_NAME}.xgb"
        prod_sha = model_dir / f"{MODEL_NAME}.xgb.sha256"
        prod_meta = model_dir / "model_metadata.json"

        backup_dir = model_dir / 'backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir.mkdir(parents=True, exist_ok=True)

        print(f"Backing up current artifacts to {backup_dir}...")
        for p in [prod_pkl, prod_xgb, prod_sha, prod_meta]:
            if p.exists():
                shutil.copy(p, backup_dir / p.name)

        print("Swapping artifacts to production...")
        shutil.move(str(new_pkl), str(prod_pkl))
        shutil.move(str(new_xgb), str(prod_xgb))
        shutil.move(str(temp_dir / f"{MODEL_NAME}.xgb.sha256"), str(prod_sha))

        # Update metadata
        metadata = {
            'model_type': 'XGBoost Binary Classifier',
            'last_trained': datetime.now().isoformat(),
            'hyperparameters': params,
            'test_performance': metrics,
            'features': feature_cols,
            'sha256': new_sha
        }
        with open(prod_meta, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print("Model successfully deployed.")

    # Cleanup temp
    shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
