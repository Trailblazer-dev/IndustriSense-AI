import pandas as pd
import numpy as np
import pickle

# Load both raw and scaled data
df_raw = pd.read_csv('data/processed/features_engineered_raw.csv')
df_scaled = pd.read_csv('data/processed/features_engineered_scaled.csv')

# Check the same 10 indices that the dashboard samples
np.random.seed(42)
sample_indices = np.random.choice(len(df_scaled), 10, replace=False)

print("Sample indices:", sample_indices)
print("\n" + "="*70)
print("Raw Tool Wear values (actual minutes):")
print(df_raw.iloc[sample_indices]['Tool wear [min]'].values)
print("\nScaled Tool Wear values (normalized):")
print(df_scaled.iloc[sample_indices]['Tool wear [min]'].values)

# Load regressor and test predictions
try:
    regressor = pickle.load(open('src/models/xgboost_wear_regressor.pkl', 'rb'))
    print("\n" + "="*70)
    print("Regressor predictions on scaled features:")
    
    FEATURE_COLS_REGRESSOR = [
        'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
        'Torque [Nm]', 'Stress Index', 'Temp Diff [K]',
        'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
    ]
    
    for i, idx in enumerate(sample_indices[:3]):
        row = df_scaled.iloc[idx]
        X = row[FEATURE_COLS_REGRESSOR].values.reshape(1, -1)
        pred = regressor.predict(X)[0]
        raw_actual = df_raw.iloc[idx]['Tool wear [min]']
        print(f"\nMachine {idx}:")
        print(f"  Actual raw: {raw_actual:.1f} min")
        print(f"  Regressor prediction: {pred:.4f}")
        print(f"  After int(): {int(pred)}")
        print(f"  RUL (253 - int(pred)): {253 - int(pred)}")
        
except Exception as e:
    print(f"Error: {e}")
