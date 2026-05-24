import numpy as np
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator

def generate_fingerprints_dynamically(df, radius=2, n_bits=2048):
    """
    Dynamically generates Morgan Fingerprints for a DataFrame of SMILES.
    Returns the X feature matrix and y target array.
    """
    morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    
    X_list = []
    y_list = []
    
    for _, row in df.iterrows():
        mol = Chem.MolFromSmiles(row['canonical_smiles'])
        if mol:
            fp = morgan_gen.GetFingerprint(mol)
            arr = np.zeros((1,))
            Chem.DataStructs.ConvertToNumpyArray(fp, arr)
            X_list.append(arr)
            y_list.append(row['active'])
            
    return np.vstack(X_list), np.array(y_list)

def smiles_to_fp(smiles, radius=2, n_bits=2048):
    """Single SMILES vectorization for Streamlit Inference."""
    morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=n_bits)
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        fp = morgan_gen.GetFingerprint(mol)
        arr = np.zeros((1,))
        Chem.DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    except Exception:
        return None