
import pandas as pd
import pickle
import os
from sklearn.preprocessing import StandardScaler

# Define paths
data_path = 'data/processed/features_engineered_raw.csv'
scaler_save_path = 'src/models/scaler.pkl'

# Features that were scaled in the notebook
features_to_scale = [
    'Air temperature [K]', 'Process temperature [K]', 
    'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]',
    'Stress Index', 'Temp Diff [K]', 
    'Temp_Diff_x_Wear', 'Speed_x_Torque'
]

def generate_scaler():
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    print("Fitting StandardScaler...")
    scaler = StandardScaler()
    scaler.fit(df[features_to_scale])
    
    print(f"Saving scaler to {scaler_save_path}...")
    with open(scaler_save_path, 'wb') as f:
        pickle.dump(scaler, f)
    
    print("Scaler persistence complete.")

if __name__ == "__main__":
    generate_scaler()
