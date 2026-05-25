# src/app/create_load_data.py
import pandas as pd
import os

def create_10k_batch():
    # Paths are now relative to the root directory (vhts-aromatase/)
    input_path = "data/raw/aromatase_raw_verified.csv"
    output_path = "data/raw/load_test_10k.csv"
    
    print("Loading baseline data...")
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find {input_path}. Make sure you are in the project root.")
        
    df = pd.read_csv(input_path)
    
    print("Oversampling to exactly 10,000 rows...")
    # sample(replace=True) allows us to randomly pick rows and duplicate them
    df_10k = df.sample(n=10000, replace=True, random_state=42).reset_index(drop=True)
    
    df_10k.to_csv(output_path, index=False)
    print(f"Success! Saved 10,000 molecule test batch to {output_path}")

if __name__ == "__main__":
    create_10k_batch()