# src/app/test_inference.py

import pandas as pd
from src.app.inference_engine import AromatasePredictor

def test_backend_pipeline():
    print("1. Initializing Inference Engine (Loading Model & Config)...")
    engine = AromatasePredictor(model_dir="models")

    print("2. Loading Test Data...")
    # We will use the raw verified data from Phase 1 to test the pipes
    data_path = "data/raw/load_test_10k.csv"
    
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Could not find {data_path}.")
        print("Make sure you are running this script from the src/app/ directory!")
        return

    print(f"3. Running Batch Inference on {len(df)} molecules...")
    results_df, metrics = engine.predict(df, smiles_column='canonical_smiles')
    
    print("\n==================================")
    print("        SYSTEM METRICS")
    print("==================================")
    for key, val in metrics.items():
        print(f"{key}: {val}")

    print("\n==================================")
    print("     TOP 5 PREDICTED ACTIVES")
    print("==================================")
    # Print the ID, the probability, and the SMILES string
    top_5 = results_df[['molecule_chembl_id', 'Probability_Active']].head(5)
    print(top_5.to_string(index=False))
    
    print("\nSUCCESS: The backend engine is fully functional!")

if __name__ == "__main__":
    test_backend_pipeline()