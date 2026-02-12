import sys
sys.path.insert(0, '.')
from app import classifier, df
import numpy as np

np.random.seed(42)
sample_indices = np.random.choice(len(df), 10, replace=False)

FEATURE_COLS_CLASSIFIER = [
    'Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]',
    'Torque [Nm]', 'Tool wear [min]', 'Stress Index', 'Temp Diff [K]',
    'Temp_Diff_x_Wear', 'Speed_x_Torque', 'is_anomaly'
]

print('FIXED VERSION - Using actual tool wear values:')
print('='*70)
for idx in sample_indices[:5]:
    row = df.iloc[idx]
    X_classifier = row[FEATURE_COLS_CLASSIFIER].values.reshape(1, -1)
    failure_prob = float(classifier.predict_proba(X_classifier)[0][1]) * 100
    tool_wear = float(row['Tool wear [min]'])
    rul = max(0, 253 - int(tool_wear))
    print(f'Machine {idx:4d}: Tool Wear={tool_wear:6.1f} min, RUL={rul:3d} min, Failure Risk={failure_prob:6.1f}%')
