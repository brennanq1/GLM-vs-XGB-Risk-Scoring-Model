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

## Engineering Decisions & Troubleshooting Log

### 1. Key Technical Decisions & Trade-Offs

#### Decision 1: Model Selection — Tweedie GLM vs. Tweedie XGBoost
* **Context:** Predicting claim amounts on auto insurance loss data (`freMTPL2`) where most policyholders have zero claims (zero-inflated) and values are heavily right-skewed.
* **Options:** Generalized Linear Model (GLM) with a Tweedie distribution and log-link vs. XGBoost Regressor using Tweedie loss (`reg:tweedie`).
* **Trade-Offs:**
  * *Tweedie GLM:* Produces clear, multiplicative rating factors that are straightforward to explain and submit for rate filings, but cannot capture multi-variable interactions without manually engineered features.
  * *Tweedie XGBoost:* Automatically identifies non-linear relationships across driver and vehicle attributes to reduce prediction error (MAE/RMSE), but functions as a less transparent model.
* **Outcome:** Used the Tweedie GLM as a clear baseline pricing model and deployed the tuned XGBoost model to the API for final risk scoring and predictions.

#### Decision 2: Decoupling SQL Scripts from Jupyter Notebooks
* **Context:** Creating tables and the aggregate modeling view (`risk_model_view`) for policy and claim records.
* **Options:** Hardcoding multi-line SQL strings inside notebook cells vs. storing SQL statements in standalone `.sql` files and executing them via Python.
* **Trade-Offs:**
  * *In-Notebook SQL:* Fast to set up initially, but clutters notebook cells, hides database changes inside notebook files, and makes reusing schema code difficult.
  * *Standalone `.sql` Files:* Requires a few lines of Python file-reading code, but keeps database logic in one place, supports standard SQL editing tools, and keeps the notebook focused on modeling.
* **Outcome:** Moved all table and view definitions into `sql/01_schema_setup.sql` and `sql/risk_model.sql`, loading and running them in Python using `cursor.executescript()`.

#### Decision 3: In-API Data Preprocessing vs. Client-Side Preprocessing
* **Context:** Serving live predictions on applicant records through a Flask endpoint (`/predict`).
* **Options:** Requiring clients to send pre-encoded feature arrays vs. accepting raw JSON applicant fields and processing them inside Flask.
* **Trade-Offs:**
  * *Client-Side:* Keeps API route logic minimal, but requires client applications to know the exact one-hot encoding columns and ordering used during training.
  * *In-API:* Adds validation and encoding logic to Flask, but allows clients to send readable, raw applicant data (like car brand and region names).
* **Outcome:** Added input checking, category mapping, and one-hot encoding directly inside `app.py` before running model inference.

---

### 2. Issues Encountered & Solutions

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **`IntegrityError: UNIQUE constraint failed: policies.ClaimNb`** | Mismatched column ordering between the pandas DataFrame and SQLite table mapped claim counts into the primary key (`IDpol`) column. | Trimmed column whitespace, fixed letter casing (`exposure` to `Exposure`), and explicitly reordered DataFrame columns in Python before running `.to_sql()`. |
| **Notebook Pointed to Outdated SQL File** | The notebook ran an old `sql/risk_model.sql` file instead of the main setup script. | Consolidated all table schemas and the `risk_model_view` definition into `sql/01_schema_setup.sql`, then updated the notebook to run that script directly. |
| **Git Push Rejected (`fetch first`)** | GitHub created an initial template file on the remote repository that was missing locally. | Overwrote the empty remote repository with the local project files using `git push -u origin main --force`. |
| **Subsequent Push Rejected on Update** | Local branch fell behind remote commits after earlier updates. | Pulled and applied local commits on top of remote changes using `git pull --rebase origin main`. |
| **Predictions Dominated by Claim Count** | Training a single Tweedie model directly on claim amounts made predictions depend almost entirely on historical `ClaimNb`, leaving little risk distinction for zero-claim drivers. | Outlined the Version 2 plan: split the pipeline into a two-part **Frequency-Severity** model (Poisson/Negative Binomial for claim counts + Gamma for claim severity). |
