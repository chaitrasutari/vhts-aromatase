# src/process_data.py

import os
import pandas as pd
import numpy as np

def clean_and_process_data():
    print("1. Loading raw verified data...")
    raw_path = "../data/raw/aromatase_raw_verified.csv"
    
    # Ensure the directory exists (fail-safe for portfolio reviewers)
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"Could not find {raw_path}. Did you run data_ingestion.py first?")
        
    df = pd.read_csv(raw_path)
    print(f"Initial records: {len(df)}")

    # ---------------------------------------------------------
    # STEP 1: Handle Duplicates
    # ---------------------------------------------------------
    print("2. Resolving chemical duplicates...")
    # If multiple labs tested the same molecule, we take the median IC50 
    # to avoid extreme outliers skewing the average.
    df_clean = df.groupby('canonical_smiles', as_index=False).agg({
        'standard_value': 'median',
        'molecule_chembl_id': 'first', # Keep the ID for reference
        'standard_units': 'first'
    })
    print(f"Unique molecules remaining: {len(df_clean)}")

    # ---------------------------------------------------------
    # STEP 2: Handle Skewness (Log Transformation)
    # ---------------------------------------------------------
    print("3. Handling skewness via pIC50 transformation...")
    # Biology scales exponentially. We convert IC50 (nM) to pIC50 (Molar)
    # pIC50 = 9 - log10(IC50). A higher pIC50 means higher potency.
    # We add 1e-10 to prevent math domain errors if standard_value is exactly 0.
    df_clean['pIC50'] = 9 - np.log10(df_clean['standard_value'] + 1e-10)

    # ---------------------------------------------------------
    # STEP 3: Delete Intermediates & Binarize
    # ---------------------------------------------------------
    print("4. Applying classification thresholds and removing intermediates...")
    # We drop the biological "grey area" (1000 nM to 10000 nM) to force a sharp decision boundary.
    # Active: IC50 < 1000 nM (pIC50 > 6.0)
    # Inactive: IC50 > 10000 nM (pIC50 < 5.0)
    
    df_filtered = df_clean[(df_clean['standard_value'] < 1000) | (df_clean['standard_value'] > 10000)].copy()
    
    # Create the binary target label (1 for Active, 0 for Inactive)
    df_filtered['active'] = (df_filtered['standard_value'] < 1000).astype(int)
    
    actives_count = df_filtered['active'].sum()
    inactives_count = len(df_filtered) - actives_count
    print(f"Data split - Actives (1): {actives_count} | Inactives (0): {inactives_count}")

    # ---------------------------------------------------------
    # STEP 4: Save to Processed Directory
    # ---------------------------------------------------------
    output_dir = "../data/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "aromatase_cleaned_binarized.csv")
    
    # Reorder columns for a clean final dataset
    final_cols = ['molecule_chembl_id', 'canonical_smiles', 'standard_value', 'pIC50', 'active']
    df_final = df_filtered[final_cols]
    
    df_final.to_csv(output_path, index=False)
    print(f"\nSUCCESS! Clean dataset saved to {output_path}")

if __name__ == "__main__":
    clean_and_process_data()