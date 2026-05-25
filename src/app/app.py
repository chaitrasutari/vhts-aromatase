# src/app/app.py

import streamlit as st
import pandas as pd
from src.app.inference_engine import AromatasePredictor

# Page Configuration
st.set_page_config(
    page_title="vHTS Aromatase Predictor", 
    page_icon="🧬",
    layout="wide"
)

@st.cache_resource
def load_engine():
    # Streamlit looks at the project root automatically
    return AromatasePredictor(model_dir="models")

engine = load_engine()

st.title("🧬 AI-Driven Virtual High-Throughput Screening")
st.markdown("Predict Aromatase (CHEMBL259) inhibitory activity using XGBoost and ECFP. Built for scalable batch inference.")

# ---------------------------------------------------------
# SINGLE MOLECULE INFERENCE
# ---------------------------------------------------------
st.subheader("⚡ Quick Predict (Single Molecule)")
single_smiles = st.text_input("Enter a SMILES string:", placeholder="e.g., N#Cc1ccc(C(c2ccc(C#N)cc2)n2cncn2)cc1")

if st.button("Predict Single Molecule"):
    if single_smiles:
        with st.spinner("Analyzing structure..."):
            prob = engine.predict(single_smiles)
            
        if prob is None:
            st.error("❌ Invalid SMILES string. Please check your syntax (e.g., unmatched parentheses).")
        else:
            if prob > 0.5:
                st.success(f"🟢 **Predicted Active** (Probability: {prob:.3f})")
            else:
                st.info(f"🔴 **Predicted Inactive** (Probability: {prob:.3f})")
    else:
        st.warning("Please enter a SMILES string first.")

st.divider()

# ---------------------------------------------------------
# BATCH INFERENCE
# ---------------------------------------------------------
st.subheader("📂 Batch Screening (CSV Upload)")

# Security Limits
MAX_ROWS = 9999
MAX_SMILES_LENGTH = 499

# UI Lock: Only allows .csv in the file explorer
uploaded_file = st.file_uploader(f"Upload CSV containing SMILES strings (Max {MAX_ROWS:,} rows)", type=["csv"])

if uploaded_file is not None:
    # SECURITY GATE 0: Backend File Extension Lock
    if not uploaded_file.name.lower().endswith('.csv'):
        st.error("❌ **Invalid File Format:** The system only accepts .csv files.")
        st.stop()
        
    input_df = pd.read_csv(uploaded_file)
    
    # SECURITY GATE 1: Batch Size Limit
    initial_count = len(input_df)
    if initial_count > MAX_ROWS:
        st.error(f"🚨 **Payload Too Large:** Your CSV contains {initial_count:,} rows. Maximum is {MAX_ROWS:,}.")
        st.stop()
        
    smiles_col = 'canonical_smiles' if 'canonical_smiles' in input_df.columns else 'SMILES'
    
    if smiles_col not in input_df.columns:
        st.error("❌ Error: CSV must contain a column named 'canonical_smiles' or 'SMILES'.")
        st.stop()
        
    # SECURITY GATE 2: SMILES Character Limit (Mitigates SMILES Bombs)
    input_df['smiles_len'] = input_df[smiles_col].astype(str).apply(len)
    safe_df = input_df[input_df['smiles_len'] <= MAX_SMILES_LENGTH].copy()
    dropped_threats = initial_count - len(safe_df)
    
    if dropped_threats > 0:
        st.warning(f"🛡️ **Security Protocol:** Dropped {dropped_threats} abnormally large strings (> {MAX_SMILES_LENGTH} characters).")
        
    with st.spinner("Vectorizing safe molecules and routing to optimal compute path..."):
        results_df, sys_metrics = engine.predict(safe_df, smiles_col)
        
    # SECURITY GATE 3: Out-of-Distribution (OOD) Circuit Breaker
    pos_preds = len(results_df[results_df['Probability_Active'] > 0.5])
    pos_rate = (pos_preds / sys_metrics['Total Processed']) * 100
    
    if pos_rate > 5.0:
        st.error("🚨 **SYSTEM CIRCUIT BREAKER TRIGGERED** 🚨")
        st.markdown(f"""
        **Fatally High Hit Rate Detected ({pos_rate:.1f}%)**
        
        Because this batch triggered a >5% positive rate, the system suspects 
        this CSV contains **Out-of-Distribution (OOD)** chemical space that 
        forces the XGBoost model to dangerously extrapolate. These results have been quarantined 
        to prevent wasted laboratory synthesis budgets.
        """)
        st.subheader("Infrastructure Health")
        st.code(f"Total Processed: {sys_metrics['Total Processed']}\nValid SMILES: {sys_metrics['Valid SMILES']}\nLatency: {sys_metrics['Latency (sec)']}s")
        
    else:
        st.success(f"✅ Guardrail Passed: {pos_rate:.2f}% Hit Rate. Data distribution is stable.")
        
        tab1, tab2 = st.tabs(["🔬 Screening Results", "📊 System Observability"])
        
        with tab1:
            st.dataframe(
                results_df.head(50).style.background_gradient(
                    subset=['Probability_Active'], cmap='Greens'
                ),
                use_container_width=True
            )
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Full Results", data=csv,
                file_name='vhts_predictions.csv', mime='text/csv',
            )
            
        with tab2:
            col1, col2, col3 = st.columns(3)
            col1.metric("Batch Size", f"{sys_metrics['Total Processed']} mols")
            col2.metric("Pipeline Latency", f"{sys_metrics['Latency (sec)']} s")
            col3.metric("Throughput", f"{sys_metrics['Throughput (mol/sec)']} mol/s")