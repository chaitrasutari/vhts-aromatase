# generate_test_data.py
import pandas as pd
import random

# =====================================================================
# 1. CHEMICAL LIBRARIES (Global definitions used by all generators)
# =====================================================================

# # The Baseline: Valid Inactives (Aspirin, Caffeine, Ibuprofen, etc.)
# INACTIVES = [
#     "CC(=O)Oc1ccccc1C(=O)O",              # Aspirin
#     "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",        # Caffeine
#     "CC(C)Cc1ccc(cc1)C(C)C(=O)O",          # Ibuprofen
#     "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C"  # Testosterone (Substrate, not inhibitor)
# ]

# # The Baseline: Truly boring, non-binding Inactives
# INACTIVES = [
#     "CC(=O)Oc1ccccc1C(=O)O",              # Aspirin
#     "CC(C)Cc1ccc(cc1)C(C)C(=O)O",          # Ibuprofen
#     "C(C1C(C(C(C(O1)O)O)O)O)O",            # Glucose (Sugar)
#     "CCCCCCC",                             # Heptane (Standard solvent)
#     "C1=CC=C(C=C1)O"                       # Phenol
# ]

# # The Baseline: Purely aliphatic, non-aromatic molecules
# INACTIVES = [
#     "CCCC",            # Butane (Lighter fluid)
#     "CCCCCC",          # Hexane (Simple solvent)
#     "CCCCCCCC",        # Octane (Gasoline component)
#     "CCOCC",           # Diethyl ether (Simple ether)
#     "C1CCCCC1"         # Cyclohexane (Non-aromatic ring)
# ]

# The Baseline: "Goldilocks" Inactives (Drug-like, but safely inactive)
INACTIVES = [
    "CC(=O)Nc1ccc(O)cc1",                  # Acetaminophen (Tylenol)
    "CC(C)Cc1ccc(cc1)C(C)C(=O)O",          # Ibuprofen (Advil)
    "CC(=O)Oc1ccccc1C(=O)O",               # Aspirin
    "COC1=CC2=C(C=C1)C=CC(=C2)C(C)C(=O)O", # Naproxen (Aleve)
    "O=C1C(O)=C(O)C(C(O)CO)O1"             # Vitamin C 
]

# The Targets: Valid Actives (Letrozole, Anastrozole, Exemestane)
ACTIVES = [
    "N#Cc1ccc(C(c2ccc(C#N)cc2)n2cncn2)cc1",       # Letrozole
    "CC(C)(C1=CC(=CC=C1)C#N)N2C=NC=N2",           # Anastrozole
    "CC12CCC3C(C1CCC2=O)CCC4=CC(=O)CCC34C=C"      # Exemestane
]

# The Anomalies: Malformed / Syntax Errors
MALFORMED = [
    "C(C(=O)O",                  # Unclosed parenthesis
    "c1cc(c",                    # Broken ring
    "THIS_IS_NOT_CHEMISTRY",     # Gibberish
    "1234567890"                 # Numbers only
]

# =====================================================================
# 2. DATA GENERATORS
# =====================================================================

def generate_standard_load_test(filename="load_test_10k.csv"):
    """
    Test 1: The standard 10,000 row load test.
    Tests the engine, the malformed string handling, and the 250-char limit.
    """
    print(f"🧬 Synthesizing Standard Load Test ({filename})...")
    dataset = []
    
    # 9,500 valid inactives and 400 valid actives (4% hit rate - passes circuit breaker)
    for _ in range(9500): dataset.append(random.choice(INACTIVES))
    for _ in range(400): dataset.append(random.choice(ACTIVES))
        
    # 50 malformed strings to test RDKit error handling
    for _ in range(50): dataset.append(random.choice(MALFORMED))
        
    # 50 massive strings to test the 250-character security gate
    massive_polymer = "C" * 300 
    massive_ring = "c1ccccc1" * 50
    for _ in range(25):
        dataset.append(massive_polymer)
        dataset.append(massive_ring)
        
    random.shuffle(dataset)
    pd.DataFrame({'canonical_smiles': dataset}).to_csv(filename, index=False)
    print("   ✅ Done! (Includes actives, inactives, malformed, and SMILES bombs)\n")


def generate_massive_dataset(filename="payload_too_large.csv"):
    """
    Test 2: The 55,000 row dataset.
    Tests the hard Row Limit security gate to prevent server OOM crashes.
    """
    print(f"🧱 Synthesizing Massive Dataset ({filename})...")
    dataset = []
    
    # Fill it with 55,000 random inactives
    for _ in range(55000): dataset.append(random.choice(INACTIVES))
    
    pd.DataFrame({'canonical_smiles': dataset}).to_csv(filename, index=False)
    print("   ✅ Done! (55,000 rows generated)\n")


def generate_low_hit_rate_dataset(filename="low_hit_rate_05.csv"):
    """
    Test 3: The highly realistic biological assay test.
    Tests the Circuit Breaker with a safe 0.5% hit rate.
    """
    print(f"🔬 Synthesizing Low Hit-Rate Dataset ({filename})...")
    dataset = []
    
    # 9,950 Inactives (99.5%) and exactly 50 Actives (0.5%)
    for _ in range(9950): dataset.append(random.choice(INACTIVES))
    for _ in range(50): dataset.append(random.choice(ACTIVES))
        
    random.shuffle(dataset)
    pd.DataFrame({'canonical_smiles': dataset}).to_csv(filename, index=False)
    print("   ✅ Done! (10,000 rows, exactly 50 actives)\n")

# =====================================================================
# 3. EXECUTION
# =====================================================================

if __name__ == "__main__":
    print("==================================================")
    print("🧪 INITIALIZING VHTS TEST DATA SYNTHESIS 🧪")
    print("==================================================\n")
    
    generate_standard_load_test()
    generate_massive_dataset()
    generate_low_hit_rate_dataset()
    
    print("==================================================")
    print("🎉 ALL TEST SUITES GENERATED SUCCESSFULLY 🎉")
    print("Ready for Streamlit UI upload testing.")