# Project Scoping Document: AI-Driven Virtual High-Throughput Screening (vHTS)

## 1. Project Objective
Build an end-to-end Machine Learning pipeline to predict whether chemical molecules (represented as SMILES strings) act as active inhibitors against a specific disease target. This tool acts as a digital filter for Virtual High-Throughput Screening, allowing chemists to evaluate 10,000+ compounds in seconds before committing to expensive wet-lab synthesis.

**Clinical Target:** Aromatase (`CHEMBL259`), a critical enzyme targeted in hormone-receptor-positive breast cancer therapies.

## 2. Tech Stack
*   **Data Ingestion & Chemistry:** Python, ChEMBL Webresource Client, RDKit
*   **Data Manipulation:** Pandas, NumPy
*   **Machine Learning:** Scikit-learn, XGBoost / Random Forest
*   **Serialization:** Joblib (optimized for NumPy arrays)
*   **Frontend UI & Observability:** Streamlit
*   **Experiment Tracking:** MLflow

## 3. Data Strategy
Data is programmatically sourced from the European Bioinformatics Institute's ChEMBL database.

*   **Extraction:** Query API for `CHEMBL259` and strictly filter for `IC50` biological assays.
*   **Standardization:** Utilize ChEMBL's standardized units (nM) and Confidence Score 9 assays (direct single-protein binding).
*   **Label Engineering (Ground Truth):**
    *   **Class 1 (Active):** IC50 < 1,000 nM
    *   **Class 0 (Inactive):** IC50 > 10,000 nM
    *   *Note: Intermediate values (1,000 - 10,000 nM) are dropped to enforce strict class boundaries and improve the model's discriminative power.*
*   **Feature Engineering:** SMILES strings are vectorized into 1D Morgan Fingerprints (ECFP) via RDKit (radius=2, 2048-bit array).

## 4. Evaluation Metrics

### A. Model Metrics (Predictive Power)
Given the severe class imbalance inherent in drug discovery (many inactives, few actives), standard accuracy is discarded in favor of:
*   **Enrichment Factor (EF) at 1%:** Target **> 3.0**. (The model must find active compounds 3x better than random selection in the top 1% of predictions).
*   **ROC-AUC:** Target **> 0.85**.
*   **Precision Priority:** High precision is prioritized over recall to minimize expensive false positives in the wet lab.

### B. System Metrics (Infrastructure Health)
*   **Throughput:** > 85 molecules / sec (optimized via Python `multiprocessing` for RDKit vectorization).
*   **P99 Inference Latency:** < 5 seconds for a batch of 10,000 unseen molecules.
*   **Peak Memory Footprint:** < 1 GB total RAM per session (managed via Streamlit `st.cache_resource` and strict garbage collection).
*   **Valid Parse Rate:** 100% graceful failure handling for malformed SMILES strings.

## 5. System Architecture
The system is divided into two operational phases:

1.  **Training Pipeline (`train_model.py`):** Ingests ChEMBL data, engineers Morgan fingerprints, trains an XGBoost classifier, tracks hyperparameter tuning via MLflow, and serializes the final artifact using `joblib`.
2.  **Inference Engine & UI (`app.py` & `inference_engine.py`):** A Streamlit application allowing users to upload a CSV of SMILES strings. The backend parallelizes RDKit vectorization across CPU cores, runs `.predict_proba()`, and returns a ranked dataframe of the highest-probability active compounds.

## 6. Observability
*   **Admin Dashboard:** A native Streamlit sub-page tracking system logs (batch latency, throughput, memory usage).
*   **Guardrail Metrics:** If the Positive Prediction Rate exceeds 5% on a new batch, the dashboard flags potential Data Drift (user uploading out-of-distribution molecules).

---

## 7. Future Scope (V2)
While V1 prioritizes rapid, lightweight CPU inference and localized data, scaling to a true clinical MLOps environment requires the following migrations:

*   **Data Version Control (DVC):** Transition from static CSVs to DVC to handle upstream ChEMBL updates and wet-lab feedback loops without overloading Git storage. Perfect reproducibility for model iterations.
*   **Continuous Training (CT):** Implement Evidently AI for automated Data Drift detection and Apache Airflow to orchestrate Champion/Challenger retraining pipelines as novel chemical spaces are explored.
*   **Graph Neural Networks (GNNs):** Migrate from 1D Morgan Fingerprints to Message Passing Neural Networks (MPNNs) via PyTorch/Chemprop to learn directly from spatial 2D molecular graphs, further maximizing the Enrichment Factor.