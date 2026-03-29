import os
import joblib
import hashlib
import warnings
from typing import Tuple, Optional

import numpy as np
try:
    import xgboost as xgb
    # Suppress XGBoost warnings about serialization/file formats globally
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")
    warnings.filterwarnings("ignore", message=".*older version of XGBoost.*")
except Exception:
    xgb = None


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            h.update(chunk)
    return h.hexdigest()


class XGBoostClassifierWrapper:
    """Adapter that provides a minimal sklearn-like interface around an XGBoost Booster.

    Provides `predict` and `predict_proba` for compatibility with existing code.
    """
    def __init__(self, booster):
        self.booster = booster

    def predict(self, X: np.ndarray) -> np.ndarray:
        if xgb is None:
            raise ImportError('xgboost is required for XGBoostClassifierWrapper')
        # Convert to numpy array to avoid feature name issues with characters like '[' and ']'
        X_arr = np.asanyarray(X)
        dm = xgb.DMatrix(X_arr)
        preds = self.booster.predict(dm, validate_features=False)
        # If binary: preds are probabilities for positive class; threshold at 0.5
        return (preds >= 0.5).astype(int)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if xgb is None:
            raise ImportError('xgboost is required for XGBoostClassifierWrapper')
        # Convert to numpy array to avoid feature name issues with characters like '[' and ']'
        X_arr = np.asanyarray(X)
        dm = xgb.DMatrix(X_arr)
        preds = self.booster.predict(dm, validate_features=False)
        # Return [[1-p, p]] per-sample
        return np.vstack([1 - preds, preds]).T


class XGBoostRegressorWrapper:
    def __init__(self, booster):
        self.booster = booster

    def predict(self, X: np.ndarray) -> np.ndarray:
        if xgb is None:
            raise ImportError('xgboost is required for XGBoostRegressorWrapper')
        # Convert to numpy array to avoid feature name issues with characters like '[' and ']'
        X_arr = np.asanyarray(X)
        dm = xgb.DMatrix(X_arr)
        preds = self.booster.predict(dm, validate_features=False)
        return preds


def load_classifier(model_dir: str) -> Tuple[Optional[object], Optional[str]]:
    """Load classifier artifact.

    Returns (model_object, sha256) where model_object provides `predict` and `predict_proba`.
    Prefers native .xgb files, then joblib, then legacy pickle.
    """
    xgb_path = os.path.join(model_dir, 'xgboost_classifier.xgb')
    joblib_path = os.path.join(model_dir, 'xgboost_classifier.joblib')
    pkl_path = os.path.join(model_dir, 'xgboost_classifier.pkl')

    if os.path.exists(xgb_path) and xgb is not None:
        sha = sha256_file(xgb_path)
        booster = xgb.Booster()
        booster.load_model(xgb_path)
        return XGBoostClassifierWrapper(booster), sha

    # Prioritize joblib over legacy pickle
    target_path = joblib_path if os.path.exists(joblib_path) else pkl_path
    if os.path.exists(target_path):
        sha = sha256_file(target_path)
        try:
            obj = joblib.load(target_path)
            # If it's an XGBClassifier sklearn wrapper, extract booster
            if hasattr(obj, 'get_booster') and xgb is not None:
                booster = obj.get_booster()
                return XGBoostClassifierWrapper(booster), sha
            return obj, sha
        except Exception as e:
            print(f"Warning: Failed to load artifact with joblib: {e}")

    return None, None


def load_regressor(model_dir: str) -> Tuple[Optional[object], Optional[str]]:
    xgb_path = os.path.join(model_dir, 'xgboost_wear_regressor.xgb')
    joblib_path = os.path.join(model_dir, 'xgboost_wear_regressor.joblib')
    pkl_path = os.path.join(model_dir, 'xgboost_wear_regressor.pkl')

    if os.path.exists(xgb_path) and xgb is not None:
        sha = sha256_file(xgb_path)
        booster = xgb.Booster()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            booster.load_model(xgb_path)
        return XGBoostRegressorWrapper(booster), sha

    target_path = joblib_path if os.path.exists(joblib_path) else pkl_path
    if os.path.exists(target_path):
        sha = sha256_file(target_path)
        try:
            obj = joblib.load(target_path)
            if hasattr(obj, 'get_booster') and xgb is not None:
                booster = obj.get_booster()
                return XGBoostRegressorWrapper(booster), sha
            return obj, sha
        except Exception as e:
            print(f"Warning: Failed to load artifact with joblib: {e}")

    return None, None
