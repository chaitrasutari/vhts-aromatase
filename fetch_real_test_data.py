import pandas as pd
import urllib.request
import os

def fetch_clinical_drugs():
    print("🌍 Reaching out to Stanford's MoleculeNet AWS S3 Bucket...")
    url = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/clintox.csv.gz"
    output_filename = "real_clinical_drugs.csv"
    
    try:
        # 1. Download the raw compressed data directly from Stanford
        print("📥 Downloading clinical data...")
        df = pd.read_csv(url, compression='gzip')
        
        # 2. The dataset uses 'smiles' instead of 'canonical_smiles'. 
        # Your Streamlit app handles both, but let's rename it to be perfectly clean.
        df = df.rename(columns={'smiles': 'canonical_smiles'})
        
        # 3. Keep only the SMILES and the FDA approval status (for our own curiosity)
        df = df[['canonical_smiles', 'FDA_APPROVED']]
        
        # 4. Clean out any missing data
        df = df.dropna(subset=['canonical_smiles'])
        
        # 5. Save to your local machine
        df.to_csv(output_filename, index=False)
        
        print(f"✅ Success! Saved {len(df)} real clinical drugs to {output_filename}")
        print("Ready to drop into Streamlit!")
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")

if __name__ == "__main__":
    fetch_clinical_drugs()