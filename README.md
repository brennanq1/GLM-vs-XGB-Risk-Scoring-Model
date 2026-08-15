# Risk-Scoring API: Tweedie GLM vs. XGBoost

## Overview
This project predicts insurance claim severity using the French Motor Third-Party Liability claims dataset (`freMTPL2`). It builds an end-to-end pipeline that ingests data via SQLite, evaluates a fine tuned Generalized Linear Model (Tweedie Regressor) and XGBoost regressor, and returns predictions via a production Flask API.

## Project Structure
* `data/`: Local directory for raw datasets (`freMTPL2freq.csv`, `freMTPL2sev.csv`) and SQLite database (`risk_model.db`).
* `sql/`: SQLite database setup scripts and data aggregation queries.
* `model_training/`: Jupyter notebook (`model_creation.ipynb`) containing Exploratory Data Analysis, feature engineering, and model evaluation.
* `production_api/`: Flask application (`app.py`) and serialized model artifacts (`.pkl`).
* `test_script.py`: Local test script to validate multi-profile API responses.

## The API
The Flask API accepts JSON payloads containing applicant driver data, handles categorical mapping and one-hot encoding internally, and returns four key metrics:

* **Predicted Claim Amount (USD)**: Model prediction output.
* **Pure Premium Relativity**: Multiplier comparing applicant risk against baseline portfolio average.
* **Risk Severity Score (1-100)**: Scaled score for rapid underwriting assessment.
* **Risk Tier**: Tiered classification ranging from Tier 0 (Low Risk) to Tier 5 (Extreme Outlier).

### Example API Response
```json
{
    "status": "success",
    "Predicted Business Risk Level": "Tier 2: Elevated Risk",
    "Predicted Claim Amount_USD": 215.35,
    "Pure Premium Relativity": 1.28,
    "Risk Severity Score 1-100": 18.5
}
```

## Running Locally

### Clone the repository:
```bash
git clone [https://github.com/brennanq1/GLM-vs-XGB-Risk-Scoring-Model.git](https://github.com/brennanq1/GLM-vs-XGB-Risk-Scoring-Model.git)
cd GLM-vs-XGB-Risk-Scoring-Model
```

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Start the Flask Server:
```
python production_api/app.py
```

### Run the Test Script:
```bash
python test_script.py
```
