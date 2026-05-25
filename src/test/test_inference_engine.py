# src/test/test_inference_engine.py

import pytest
import pandas as pd
import os
from unittest.mock import patch
from src.app.inference_engine import AromatasePredictor

# ---------------------------------------------------------
# FIXTURES (Setup before each test)
# ---------------------------------------------------------
@pytest.fixture
def engine():
    """
    Initializes the engine with a tiny threshold of 10 for testing.
    This allows us to test parallel routing without needing 10,000 rows.
    """
    os.environ["VHTS_PARALLEL_THRESHOLD"] = "10"
    return AromatasePredictor(model_dir="models")

@pytest.fixture
def valid_smiles():
    return "N#Cc1ccc(C(c2ccc(C#N)cc2)n2cncn2)cc1" # Letrozole

@pytest.fixture
def malformed_smiles():
    return "C(C(=O)O" # Unmatched parenthesis

# ---------------------------------------------------------
# THE TESTS
# ---------------------------------------------------------

def test_single_smiles_valid(engine, valid_smiles):
    """Test User 1: Quick Predict with valid chemistry."""
    probability = engine.predict(valid_smiles)
    
    assert probability is not None
    assert 0.0 <= probability <= 1.0

def test_single_smiles_invalid(engine, malformed_smiles):
    """Test User 2: Quick Predict with syntax error."""
    probability = engine.predict(malformed_smiles)
    
    # RDKit should catch the error and return None, not crash
    assert probability is None

def test_sequential_routing(engine, valid_smiles):
    """Test User 3: Small CSV (<10 rows). Must route to Sequential."""
    # Create a tiny dataframe of 5 molecules
    df = pd.DataFrame({'canonical_smiles': [valid_smiles] * 5})
    
    # We "spy" on the internal _run_batch method to see how it was called
    with patch.object(engine, '_run_batch', wraps=engine._run_batch) as spy:
        results_df, metrics = engine.predict(df)
        
        # Verify it was called exactly once
        spy.assert_called_once()
        # Verify it specifically told _run_batch to NOT use parallel
        assert spy.call_args[1]['use_parallel'] is False
        
        # Verify the actual output is correct
        assert len(results_df) == 5
        assert metrics['Total Processed'] == 5

def test_parallel_routing(engine, valid_smiles):
    """Test User 4: Large CSV (>=10 rows). Must route to Parallel."""
    # Create a dataframe of 15 molecules (exceeds our test threshold of 10)
    df = pd.DataFrame({'canonical_smiles': [valid_smiles] * 15})
    
    with patch.object(engine, '_run_batch', wraps=engine._run_batch) as spy:
        results_df, metrics = engine.predict(df)
        
        spy.assert_called_once()
        # Verify the Smart Router successfully flipped the parallel switch to True
        assert spy.call_args[1]['use_parallel'] is True
        
        assert len(results_df) == 15
        assert metrics['Total Processed'] == 15

def test_invalid_input_type(engine):
    """Test User 5: Passing completely wrong data types."""
    with pytest.raises(ValueError, match="Input must be a SMILES string or a Pandas DataFrame"):
        engine.predict(["C1=CC=CC=C1", "CCO"]) # Passing a list instead of string/df