# src/app/inference_engine.py

import os
import time
import joblib
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from joblib import Parallel, delayed
from dotenv import load_dotenv

# Load local .env file if it exists (fails silently in production)
load_dotenv()

# ---------------------------------------------------------
# WORKER FUNCTION (Bypasses Pickling Limit)
# ---------------------------------------------------------
_worker_morgan_gen = None

def _smiles_to_fp_worker(smiles, radius, bits):
    global _worker_morgan_gen
    if _worker_morgan_gen is None:
        _worker_morgan_gen = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=bits)
        
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        fp = _worker_morgan_gen.GetFingerprint(mol)
        arr = np.zeros((1,))
        Chem.DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    except Exception:
        return None

# ---------------------------------------------------------
# PREDICTOR CLASS
# ---------------------------------------------------------
class AromatasePredictor:
    def __init__(self, model_dir="models"):
        self.model = joblib.load(f"{model_dir}/aromatase_xgb_production.joblib")
        self.config = joblib.load(f"{model_dir}/production_config.joblib")
        
        # Load threshold from environment, default to 250 if not set
        env_threshold = os.getenv("VHTS_PARALLEL_THRESHOLD", "250")
        self.parallel_threshold = int(env_threshold)

    def predict(self, data, smiles_column='canonical_smiles'):
        """Unified routing function."""
        if isinstance(data, str):
            return self._predict_single(data)
            
        elif isinstance(data, pd.DataFrame):
            total_molecules = len(data)
            if total_molecules < self.parallel_threshold:
                return self._run_batch(data, smiles_column, use_parallel=False)
            else:
                return self._run_batch(data, smiles_column, use_parallel=True)
        else:
            raise ValueError("Input must be a SMILES string or a Pandas DataFrame.")

    def _predict_single(self, smiles):
        r = self.config['radius']
        b = self.config['bits']
        fp = _smiles_to_fp_worker(smiles, r, b)
        if fp is None:
            return None
        X_matrix = fp.reshape(1, -1)
        return self.model.predict_proba(X_matrix)[0, 1]

    def _run_batch(self, df, smiles_col, use_parallel):
        start_time = time.perf_counter()
        total_molecules = len(df)
        r = self.config['radius']
        b = self.config['bits']
        
        if use_parallel:
            fp_list = Parallel(n_jobs=-1)(
                delayed(_smiles_to_fp_worker)(smiles, r, b) for smiles in df[smiles_col]
            )
        else:
            fp_list = [
                _smiles_to_fp_worker(smiles, r, b) for smiles in df[smiles_col]
            ]
            
        df['fingerprint'] = fp_list
        valid_df = df.dropna(subset=['fingerprint']).copy()
        valid_parses = len(valid_df)
        
        X_matrix = np.vstack(valid_df['fingerprint'].values)
        probabilities = self.model.predict_proba(X_matrix)[:, 1]
        valid_df['Probability_Active'] = probabilities
        
        end_time = time.perf_counter()
        latency_seconds = end_time - start_time
        throughput = total_molecules / latency_seconds if latency_seconds > 0 else 0
        parse_rate = (valid_parses / total_molecules) * 100
        
        results_df = valid_df.drop(columns=['fingerprint']).sort_values(
            by='Probability_Active', ascending=False
        )
        
        metrics = {
            "Total Processed": total_molecules,
            "Valid SMILES": valid_parses,
            "Parse Success Rate": f"{parse_rate:.1f}%",
            "Latency (sec)": f"{latency_seconds:.2f}",
            "Throughput (mol/sec)": f"{throughput:.0f}"
        }
        
        return results_df, metrics