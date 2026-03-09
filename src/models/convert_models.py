"""Conversion utilities to convert existing pickled XGBoost sklearn wrappers
to native XGBoost booster files (.xgb) and compute SHA256 checksums.

Usage:
    python convert_models.py

This script attempts to load `xgboost_classifier.pkl` and
`xgboost_wear_regressor.pkl` (if present), extract their boosters and
save `*.xgb` versions alongside a `*.sha256` file.
"""
import os
import pickle
from src.models.model_utils import sha256_file
import xgboost as xgb


def convert(model_dir: str):
    conversions = []

    pairs = [
        ('xgboost_classifier.pkl', 'xgboost_classifier.xgb'),
        ('xgboost_wear_regressor.pkl', 'xgboost_wear_regressor.xgb')
    ]

    for pkl_name, xgb_name in pairs:
        pkl_path = os.path.join(model_dir, pkl_name)
        xgb_path = os.path.join(model_dir, xgb_name)
        sha_path = xgb_path + '.sha256'

        if not os.path.exists(pkl_path):
            print(f"Source not found: {pkl_path}")
            continue

        try:
            with open(pkl_path, 'rb') as f:
                obj = pickle.load(f)

            # If sklearn wrapper with get_booster
            booster = None
            if hasattr(obj, 'get_booster'):
                booster = obj.get_booster()
            elif isinstance(obj, xgb.Booster):
                booster = obj

            if booster is None:
                print(f"No booster found inside {pkl_name}; skipping conversion.")
                continue

            booster.save_model(xgb_path)
            sha = sha256_file(xgb_path)
            with open(sha_path, 'w') as s:
                s.write(sha)

            conversions.append((pkl_path, xgb_path, sha))
            print(f"Converted {pkl_path} -> {xgb_path}, sha={sha}")

        except Exception as e:
            print(f"Failed to convert {pkl_path}: {e}")

    return conversions


if __name__ == '__main__':
    model_dir = os.path.join(os.path.dirname(__file__), '')
    convert(model_dir)
