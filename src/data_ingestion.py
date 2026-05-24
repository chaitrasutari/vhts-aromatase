# src/data_ingestion.py

import os
import pandas as pd
from chembl_webresource_client.new_client import new_client


def fetch_and_clean_aromatase_data():
    """
    Fetches Aromatase (CHEMBL1978) IC50 data from ChEMBL, applies strict
    quality filters, and saves the raw verified data to CSV.
    """
    target_id = "CHEMBL1978"

    print(f"1. Connecting to ChEMBL API for target: {target_id}")
    activity = new_client.activity
    assay = new_client.assay

    # Query for IC50 assays only
    query = activity.filter(target_chembl_id=target_id, standard_type="IC50")

    print("2. Downloading records (this may take 2-5 minutes)...")
    records = list(query)
    df = pd.DataFrame(records)
    print(f"Downloaded {len(df)} total raw records.")

    if df.empty:
        raise ValueError(f"No IC50 records found for target {target_id}.")

    print("3. Downloading assay confidence metadata...")
    assay_records = list(
        assay.filter(target_chembl_id=target_id).only(
            ["assay_chembl_id", "confidence_score"]
        )
    )
    assay_df = pd.DataFrame(assay_records)

    if assay_df.empty or "confidence_score" not in assay_df.columns:
        raise ValueError("Could not retrieve assay confidence scores from ChEMBL.")

    assay_df = assay_df[["assay_chembl_id", "confidence_score"]].drop_duplicates()
    df = df.merge(assay_df, on="assay_chembl_id", how="left")

    # 3. Select essential columns
    columns_to_keep = [
        'molecule_chembl_id',
        'canonical_smiles',
        'standard_type',
        'standard_value',
        'standard_units',
        'confidence_score',
        'data_validity_comment'
    ]
    df = df[columns_to_keep]

    # 4. Strict Quality Assurance Filtering
    print("4. Applying Data Quality & Confidence filters...")

    # Filter A: Drop rows missing critical data (SMILES or the actual IC50 value)
    df = df.dropna(subset=['canonical_smiles', 'standard_value', 'confidence_score'])

    # Filter B: Confidence Score must be exactly 9 (direct single-protein binding)
    # ChEMBL serves this from assay metadata, sometimes as a string.
    df['confidence_score'] = df['confidence_score'].astype(int)
    df = df[df['confidence_score'] == 9]

    # Filter C: Data validity comment must be null (no flagged errors from ChEMBL)
    df = df[df['data_validity_comment'].isnull()]

    # Filter D: Ensure standard units are exactly 'nM' (nanomolar) to prevent unit mixing
    df = df[df['standard_units'] == 'nM']

    # 5. Clean up types and reset index
    df['standard_value'] = df['standard_value'].astype(float)
    df = df.drop(columns=['data_validity_comment']) # Drop it since they are all null now
    df = df.reset_index(drop=True)

    print(f"5. Quality filtering complete. {len(df)} high-quality records remain.")

    # 6. Save to raw data directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(project_root, "data", "raw")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "aromatase_raw_verified.csv")
    df.to_csv(output_path, index=False)
    print(f"6. Data successfully saved to {output_path}")


if __name__ == "__main__":
    fetch_and_clean_aromatase_data()
