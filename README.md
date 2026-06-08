# AI-Driven Virtual High-Throughput Screening (vHTS)

An enterprise-grade Virtual High-Throughput Screening (vHTS) pipeline designed to predict human Aromatase inhibitory activity. The project combines ChEMBL data ingestion, RDKit molecular fingerprints, an XGBoost model, Streamlit inference UI, smart compute routing, and guardrails for safer batch screening.

![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)
![Python 3.10](https://img.shields.io/badge/Python-3.10-blue)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-orange)
![RDKit](https://img.shields.io/badge/Chemoinformatics-RDKit-green)

---

## Key Architectural Features

### 1. Smart Compute Routing and Multi-Core Parallelism

The inference engine uses workload-aware routing to keep small predictions responsive while scaling larger batches efficiently.

- **Single molecules:** Bypasses unnecessary batch overhead for quick UI feedback.
- **Small batches:** Uses sequential processing to avoid multiprocessing overhead.
- **Large batches:** Uses multi-core `joblib` worker pools for RDKit fingerprint generation and model inference.

RDKit objects can be awkward across multiprocessing boundaries, so worker functions instantiate Morgan fingerprint generators inside each worker process.

### 2. Security and Threat Mitigation

Chemoinformatics endpoints can be vulnerable to malformed payloads and expensive molecule parsing. The application layer applies strict intake controls:

- **CSV-only uploads:** Accepts structured molecule tables and blocks unsupported files.
- **Payload size limits:** Caps uploads to prevent excessive memory usage during XGBoost matrix construction.
- **SMILES length guardrail:** Drops overly long SMILES strings before RDKit parsing to reduce algorithmic complexity risk.
- **Graceful invalid-input handling:** Malformed SMILES are rejected without crashing the app.

### 3. Biological Guardrails

Tree-based models are strong interpolators but can be unreliable on molecules far outside the training distribution. The app includes an out-of-distribution circuit breaker:

- If a batch produces a positive prediction rate above **5.0%**, the UI blocks the result set.
- This prevents suspiciously high hit-rate batches from being treated as reliable wet-lab candidates.
- The guardrail is designed for conservative virtual screening where false positives are expensive.

---

<img width="1904" height="537" alt="pako_eNp9Vdty4kYQ_ZWuSXlfFggXC7x6cCoIY7sCWWcV7yYRVGosNTBrMaOdGTlmKf97WjcQKhI9SHM5PdPn9EV7FqoImcvWmicb-H2ykEDPxQU8GtRwL5PUmmLNpE8FyIsFSgtB-b2XFvWKh7gscNnzeB_4ViPfxsLCF3yihdpufurPgS_kOkbw5_ezGx8IT_MltNvXhG6Ax8GY25Cu9j" src="https://github.com/user-attachments/assets/31032074-169e-4218-b476-eafd39f422df" />


## Tech Stack

- **Model:** XGBoost classifier
- **Chemoinformatics:** RDKit Morgan fingerprints / ECFP
- **Data:** ChEMBL Webresource Client, Pandas, NumPy
- **Parallelism:** Joblib multiprocessing
- **UI:** Streamlit
- **Testing:** Pytest and Streamlit `AppTest`
- **Experiment tracking:** MLflow

---

## Repository Layout

```text
.
|-- docs/
|-- notebooks/
|-- src/
|   |-- app/
|   |   |-- app.py
|   |   |-- create_load_data.py
|   |   `-- inference_engine.py
|   |-- models/
|   |   |-- promote_model.py
|   |   `-- xgboost_experimentation.py
|   |-- test/
|   |   |-- test_app.py
|   |   |-- test_inference.py
|   |   `-- test_inference_engine.py
|   |-- utils/
|   |   |-- features.py
|   |   `-- metrics.py
|   |-- data_ingestion.py
|   `-- process_data.py
|-- fetch_real_test_data.py
|-- generate_test_data.py
|-- pytest.ini
|-- requirements.txt
`-- README.md
```

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/chaitrasutari/vhts-aromatase.git
cd vhts-aromatase
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Usage

### Run the Streamlit application

```bash
python -m streamlit run src/app/app.py
```

### Configure the parallelization threshold

The inference engine can use an environment variable to decide when to switch from sequential processing to parallel processing.

PowerShell:

```powershell
$env:VHTS_PARALLEL_THRESHOLD="250"
```

Bash:

```bash
export VHTS_PARALLEL_THRESHOLD=250
```

---

## Data Pipeline

### Fetch and clean ChEMBL Aromatase activity data

```bash
python src/data_ingestion.py
```

This writes the cleaned assay data to:

```text
data/raw/aromatase_raw_verified.csv
```

### Process data for modeling

```bash
python src/process_data.py
```

### Run XGBoost experimentation

```bash
python src/models/xgboost_experimentation.py
```

### Promote the selected model

```bash
python src/models/promote_model.py
```

---

## Testing and Test Data

### Run the test suite

```bash
python -m pytest -v
```

### Generate synthetic test data

```bash
python generate_test_data.py
```

### Fetch real-world clinical test data

```bash
python fetch_real_test_data.py
```

The generated CSVs can be uploaded into the Streamlit UI to evaluate load handling, low-hit-rate batches, oversized payload behavior, and real clinical-drug screening scenarios.

---

## Git Hygiene

The repository should track source code, documentation, tests, and lightweight configuration. It should not track local environments, caches, generated model artifacts, MLflow runs, or large generated datasets unless they are intentionally versioned.

Recommended ignored paths include:

```gitignore
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
data/
models/
mlruns/
*.joblib
*.pkl
```
