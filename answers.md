# Certificate Program AIML - 12-Minute Video Demo Commands

## Overview
These are the commands needed to successfully demonstrate all 8 tasks for the 12-minute video. Assume SETUP.md Phase 1 (environment and tests) has already been executed.

---

## Task 1: Data Pipeline

### Goal
Show data source, execute pipeline command, and display processed dataset with validation results.

### Commands

**Step 1: Verify configuration**
```powershell
# PowerShell
cat config/config.yaml | Select-String -Pattern 'year|month|data_dir'
```
```bash
# Bash
grep -E 'year|month|data_dir' config/config.yaml
```

**Step 2: Run the pipeline (skip download if data already exists)**
```powershell
# PowerShell - Full run with download
.\.venv\Scripts\python.exe -m scripts.run_pipeline --year 2024 --month 1

# Or skip download if data exists
.\.venv\Scripts\python.exe -m scripts.run_pipeline --skip-download
```
```bash
# Bash - Full run with download
.venv/bin/python -m scripts.run_pipeline --year 2024 --month 1

# Or skip download if data exists
.venv/bin/python -m scripts.run_pipeline --skip-download
```

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **Pipeline Summary** | `data/processed/pipeline_summary.json` | Cleaning counts (raw, retained, removed), reasons for removal, configuration used |
| **Clean Trips** | `data/processed/trips_clean.parquet` | 2.7M validated taxi trips ready for modeling |
| **Hourly Demand** | `data/processed/demand_hourly.parquet` | Pickup counts aggregated by zone and hour (188K zone-hour combinations) |
| **Fare Features** | `data/features/fare_features.parquet` | 16-column feature table with distance, duration, zones, time features (2.7M rows) |
| **Demand Features** | `data/features/demand_features.parquet` | 23-column feature table with lags and rolling windows (145K rows) |
| **Train/Val/Test Splits** | `data/features/{demand,fare}_{train,val,test}.parquet` | 6 files split chronologically for modeling |

### Quick Validation
```powershell
# Verify key artifacts exist
Test-Path data\processed\pipeline_summary.json
Test-Path data\features\fare_features.parquet
Test-Path data\features\demand_features.parquet
```

---

## Task 2: Model Training

### Goal
Show training code, completed training logs, evaluation metrics, and saved model artifact.

### Commands

**Step 1: Verify training inputs exist**
```powershell
# PowerShell
Test-Path data\features\fare_train.parquet
Test-Path data\features\fare_val.parquet
Test-Path data\features\fare_test.parquet
Test-Path data\features\demand_train.parquet
```

**Step 2: Train both demand and fare models with 1 trial (fast for demo)**
```powershell
# PowerShell - Full training with registration
.\.venv\Scripts\python.exe -m scripts.train_models --n-trials 1

# Or train without registration (to keep registry clean)
.\.venv\Scripts\python.exe -m scripts.train_models --n-trials 1 --no-register
```
```bash
# Bash
.venv/bin/python -m scripts.train_models --n-trials 1
```

**Step 3: Start MLflow UI in separate terminal (optional)**
```powershell
.\.venv\Scripts\python.exe -m mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```
```bash
.venv/bin/python -m mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```
Open: http://127.0.0.1:5000

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **MLflow Database** | `mlflow.db` | SQLite tracking store with all run metadata |
| **Model Artifacts** | `mlruns/{experiment_id}/{run_id}/artifacts/` | Serialized XGBoost/LightGBM models, hyperparameters, validation metrics |
| **Registered Models** | MLflow Registry | `taxi-demand-forecaster` and `taxi-fare-predictor` with version 1+ |
| **SHAP Plots** | `artifacts/responsible/demand_shap_summary.png`, `artifacts/responsible/fare_shap_summary.png` | Feature importance visualizations |
| **Model Cards** | `docs/model_cards/demand.md`, `docs/model_cards/fare.md` | Model documentation with metrics, limitations, intended use |

### Key Metrics to Display
```
Demand Model: RMSE, MAE, MAPE, R²
Fare Model: RMSE, MAE, MAPE, R²
```

---

## Task 3: Model Serving - Live API Inference

### Goal
Demonstrate one live API inference request and batch inference execution with predictions.

### Commands

**Step 1: Prepare portable registry (only needed for Docker route)**
```powershell
# Optional - for Docker/container deployment
.\.venv\Scripts\python.exe scripts\make_mlflow_portable.py `
    --src mlflow.db `
    --dest mlflow.container.db `
    --new-base "file:///app/mlruns"
```

**Step 2: Start the API (choose one route)**

**Route A: Docker (if Docker available)**
```powershell
# PowerShell
docker version
$env:TAXI_API_HOST_PORT = "8001"
$env:MLFLOW_UI_HOST_PORT = "5001"
docker compose -f docker/docker-compose.yml up --build
```
API: http://localhost:8001
MLflow UI: http://localhost:5001

**Route B: Local Python (no Docker required)**
```powershell
# PowerShell
.\.venv\Scripts\python.exe -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```
```bash
# Bash
.venv/bin/python -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```
API: http://127.0.0.1:8000

**Step 3: Verify API health**
```powershell
# PowerShell
Invoke-RestMethod http://localhost:8001/health
```
```bash
# Bash
curl --fail --silent --show-error http://localhost:8001/health
```

**Expected response:**
```json
{
  "status": "ok",
  "demand_model_loaded": true,
  "fare_model_loaded": true,
  "history_hours": 744,
  "zones": 253
}
```

**Step 4: Make a live fare prediction**
```powershell
# PowerShell - Fare prediction
$body = @{
    trip_distance = 3.5
    PULocationID = 186
    DOLocationID = 43
    passenger_count = 2
    trip_duration_min = 12
    hour = 14
    day_of_week = 2
    is_holiday = 0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8001/predict/fare" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Step 5: Batch forecasting**
```powershell
# PowerShell
.\.venv\Scripts\python.exe -m scripts.batch_forecast --horizon 3
```
```bash
# Bash
.venv/bin/python -m scripts.batch_forecast --horizon 3
```

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **API Response (live)** | HTTP response | Real-time prediction with confidence bounds |
| **Batch Predictions** | `predictions.db` | SQLite database with forecast results, timestamps, zones |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI showing all endpoints |

### What to Demo
1. Health check response (shows both models loaded)
2. One valid fare prediction
3. One valid demand prediction
4. One invalid request (shows validation errors)

---

## Task 4: CI/CD Architecture

### Goal
Show GitHub Actions (or equivalent) workflow with successful run and deployed service status.

### Commands

**Step 1: Inspect local CI script**
```powershell
# View the local CI/CD pipeline definition
type scripts\ci_local.ps1
```
```bash
# View the local CI/CD pipeline
cat scripts/ci_local.ps1
```

**Step 2: Run local CI checks (linting, tests, coverage)**
```powershell
# PowerShell - Full CI with Terraform
.\scripts\ci_local.ps1

# Or without Terraform if not installed
.\scripts\ci_local.ps1 -NoTerraform
```
```bash
# Bash - Requires PowerShell 7
pwsh -File ./scripts/ci_local.ps1 -NoTerraform
```

**Step 3: Inspect hosted CI configuration**
```powershell
# View the CodeBuild buildspec for cloud deployment
type buildspec.yml

# View Terraform CI/CD infrastructure
type infra\terraform\cicd.tf
```

**Step 4: Check CodeBuild status (if AWS available)**
```powershell
# PowerShell - AWS CodeBuild status
$Region = "us-east-1"
$Project = terraform -chdir=infra/terraform output -raw cicd_project_name
$BuildId = aws codebuild list-builds-for-project `
    --project-name $Project --region $Region --sort-order DESCENDING `
    --query "ids[0]" --output text
aws codebuild batch-get-builds --ids $BuildId --region $Region `
    --query "builds[0].{Status:buildStatus,Phase:currentPhase}"
```

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **Local CI Results** | Console output | Ruff lint results, pytest pass/fail, coverage percentage |
| **Buildspec** | `buildspec.yml` | Cloud CI/CD stages: build, push to ECR, ECS deployment |
| **Terraform** | `infra/terraform/cicd.tf` | CodeBuild project, ECR repository, IAM roles |

### CI/CD Pipeline Stages
1. **Lint** (Ruff): Check code style
2. **Tests** (pytest): Run unit/integration tests
3. **Coverage**: Verify minimum coverage threshold
4. **Terraform** (local): Validate infrastructure-as-code
5. **Build** (cloud): Docker image creation
6. **Push** (cloud): ECR image push
7. **Deploy** (cloud): ECS service update

### Important Notes for Video
- Local CI does NOT include Docker or deployment
- Cloud CI runs in AWS CodeBuild (show buildspec.yml lines only, don't execute)
- Show line numbers in buildspec.yml where Docker build, ECR push, and ECS update occur
- Mention: "No ECS stability waiter in buildspec - deployment requested, not verified"

---

## Task 5: Monitoring Drift

### Goal
Show monitoring metrics and execute drift detection report with alert interpretation.

### Commands

**Step 1: Generate drift detection report**
```powershell
# PowerShell
.\.venv\Scripts\python.exe -m scripts.monitoring.demo_drift_report --problem all --mode drift --seed 42
```
```bash
# Bash
.venv/bin/python -m scripts.monitoring.demo_drift_report --problem all --mode drift --seed 42
```

**Step 2: View drift reports**
```powershell
# PowerShell - Read JSON output
Get-Content artifacts\drift\demand_drift_metrics.json -Raw | ConvertFrom-Json
Get-Content artifacts\drift\fare_drift_metrics.json -Raw | ConvertFrom-Json
```
```bash
# Bash
cat artifacts/drift/demand_drift_metrics.json | jq .
cat artifacts/drift/fare_drift_metrics.json | jq .
```

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **Demand Drift** | `artifacts/drift/demand_drift_metrics.json` | PSI & KS statistics for 20 demand features |
| **Fare Drift** | `artifacts/drift/fare_drift_metrics.json` | PSI & KS statistics for 14 fare features |

### What the Reports Mean - Script Explanation for Video

#### Demand Drift Report
```
Key metrics to highlight:
- "drifted": true/false (overall alert status)
- "n_features": 20 (number of monitored features)
- "psi_threshold": 0.2 (sensitivity setting)

For each flagged feature:
- "PSI" (Population Stability Index): 
  * < 0.1: No significant drift
  * 0.1-0.2: Small drift (monitor)
  * > 0.2: Significant drift (investigate)
  
Example: lag_2 has PSI=13.66 (68× the threshold)
Interpretation: "This feature's distribution shifted dramatically. 
The model may struggle because it's outside the training distribution."

- "KS statistic": 0.95+ means the two distributions don't overlap at all
- "p-value": Near 0 means the drift is statistically significant
```

#### Fare Drift Report
```
Similar to demand, but for location and trip-level features.

Example: PULocationID has PSI=8.63
Interpretation: "Pickup locations in current data differ greatly 
from training data. Could indicate service area expansion, 
geographically-clustered outages, or data collection issues."
```

#### Response Decision (What to Say in Video)
```
"When drift is detected:
1. DO NOT retrain automatically
2. INVESTIGATE the cause:
   - Is this a real business change (e.g., holiday surge)?
   - Or a data error (pipeline bug, counter reset)?
3. IF real: Monitor model performance on this segment
4. IF error: Fix data pipeline, then retrain

The synthetic drift here (2.5× multiplier) is extreme. 
Real drift is often more subtle and requires domain judgment."
```

---

## Task 6: Responsible AI - Explainability & Bias

### Goal
Show one responsible AI analysis (explainability, bias evaluation) with results.

### Commands

**Step 1: Generate responsible AI analysis**
```powershell
# PowerShell
.\.venv\Scripts\python.exe -m scripts.responsible.run_analysis
```
```bash
# Bash
.venv/bin/python -m scripts.responsible.run_analysis
```

**Step 2: View generated artifacts**
```powershell
# List all responsible AI outputs
Get-ChildItem artifacts\responsible\ -Recurse
Get-ChildItem docs\model_cards\
```

### Output Locations & Meanings

| Output | Path | What it shows |
|--------|------|---------------|
| **SHAP Summary - Demand** | `artifacts/responsible/demand_shap_summary.png` | Feature importance beeswarm plot (23 features) |
| **SHAP Summary - Fare** | `artifacts/responsible/fare_shap_summary.png` | Feature importance beeswarm plot (16 features) |
| **Fairness Report - Demand** | `artifacts/responsible/demand_fairness.json` | Subgroup error comparisons (borough, time, airport) |
| **Fairness Report - Fare** | `artifacts/responsible/fare_fairness.json` | Subgroup error comparisons (borough, time, airport) |
| **Model Cards** | `docs/model_cards/demand.md`, `docs/model_cards/fare.md` | Limitations, intended use, monitoring recommendations |

### What to Explain in Video - SHAP Analysis

#### SHAP Beeswarm Plot Reading
```
For the fare model (example):

1. Vertical axis = Feature importance (mean absolute SHAP value)
   "trip_distance has the strongest influence on predictions"

2. Horizontal axis = Direction and magnitude of influence
   "When trip_distance is high (red dots), predicted fare increases
    When trip_distance is low (blue dots), predicted fare decreases"

3. Color = Feature value (blue=low, red=high)
   "This is just a color scale, NOT a quality indicator
    Red doesn't mean 'good', blue doesn't mean 'bad'"

4. Dot density = How often that influence level occurs
   "Most predictions cluster near the baseline, 
    but outliers can swing predictions significantly"
```

#### What This DOES and DOESN'T Show
```
✓ DOES show: Which features the model heavily relies on
✗ DOESN'T show: Whether the model is fair or causal

For example:
- trip_distance is important → makes sense (longer trips cost more)
- But this doesn't prove distance CAUSES fares;
  it just shows the model uses distance as a signal
```

### What to Explain - Fairness Analysis

#### Fairness Report Structure
```
For each subgroup (e.g., airport vs. non-airport trips):
- n: How many test samples in this group
- RMSE: Average prediction error (in dollars)
- MAE: Absolute error
- MAPE: Percentage error
- disparity_ratio: Worst group RMSE / Best group RMSE

Example output:
"Airport trips: RMSE=$5.20, Non-airport: RMSE=$2.80
 Ratio: 5.20/2.80 = 1.86 → FLAGGED (> 1.5 threshold)"
```

#### What to Say About Flagged Disparities
```
"A 1.86× ratio means the model is less accurate on airport trips.
This could be because:
1. Airport trips are longer and rarer in training data
2. There are more confounding factors (taxi demand, traffic)
3. Data quality differs for airport routes

This flag means INVESTIGATE, not REJECT the model.
Next step: gather more airport data or engineer better features.
Fairness is not a binary; it's a measured disparity to minimize."
```

---

## Task 7: Dashboard

### Goal
Open the functional dashboard and demonstrate one interaction using actual project outputs.

### Commands

**Step 1: Install dashboard dependencies**
```powershell
# PowerShell
.\.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
```
```bash
# Bash
.venv/bin/python -m pip install -r requirements-dashboard.txt
```

**Step 2: Ensure API is running (from Task 3)**
```powershell
# From another terminal, keep API running:
.\.venv\Scripts\python.exe -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```

**Step 3: Start dashboard**
```powershell
# PowerShell
$env:API_BASE_URL = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```
```bash
# Bash
export API_BASE_URL="http://127.0.0.1:8000"
.venv/bin/python -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

**Step 4: Open in browser**
Open: http://127.0.0.1:8501

### Dashboard Panel Sources & What They Show

| Panel | Source | What to demo |
|-------|--------|-------------|
| **Health Check** | Live API call | Shows both models loaded, history window, zones |
| **Fare Predictor** | API /predict/fare endpoint | Make a prediction, show output |
| **Demand Forecaster** | API /predict/demand endpoint | Forecast pickups for a zone |
| **Explainability** | Local SHAP PNG files | Display feature importance plot |
| **Fairness/Bias** | Local fairness JSON + model card | Show subgroup error comparisons |
| **Drift Monitor** | Local drift JSON | Display flagged features |

### What to Demonstrate in Video
1. **Dashboard loads** - No errors
2. **Health panel** - Both models ready
3. **One prediction** - Enter fare or demand input, show output with confidence
4. **One explanation** - Click SHAP plot, explain top 3 features
5. **One fairness check** - Show a subgroup with disparity warning

---

## Task 8: Golden Path - End-to-End Execution

### Goal
Show clean setup instructions, trigger end-to-end execution, and demonstrate traceable evidence that all stages completed.

### Full Setup Commands (SETUP.md)

**Phase 1: Environment & Tests**
```powershell
# PowerShell
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```

**Phase 2: Data Pipeline**
```powershell
.\.venv\Scripts\python.exe -m scripts.run_pipeline --year 2024 --month 1
```

**Phase 3: Training & Registry**
```powershell
.\.venv\Scripts\python.exe -m scripts.train_models --n-trials 1
```

**Phase 4: API**
```powershell
.\.venv\Scripts\python.exe -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
# In another terminal:
curl http://127.0.0.1:8000/health
```

**Phase 5: Batch & Analysis**
```powershell
.\.venv\Scripts\python.exe -m scripts.batch_forecast --horizon 3
.\.venv\Scripts\python.exe -m scripts.responsible.run_analysis
.\.venv\Scripts\python.exe -m scripts.monitoring.demo_drift_report --problem all --mode drift
```

**Phase 6: Dashboard**
```powershell
$env:API_BASE_URL = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501
```

### Traceable Evidence - What to Screenshot/Show

**After each phase, capture:**

| Phase | Evidence File(s) | Verification Command |
|-------|------------------|----------------------|
| Tests | Console output | `.venv/bin/python -m pytest -v` |
| Pipeline | `data/processed/pipeline_summary.json` | `cat data/processed/pipeline_summary.json \| jq` |
| Training | MLflow UI or `artifacts/responsible/fare_shap_summary.png` | Visit `http://127.0.0.1:5000` |
| API | Health response | `curl http://127.0.0.1:8000/health \| jq` |
| Analysis | `artifacts/responsible/` (3+ files) | `ls -la artifacts/responsible/` |
| Dashboard | Browser screenshot | http://127.0.0.1:8501 |

### Completion Checklist for Video
- [ ] Python 3.11 version confirmed
- [ ] Virtual environment created, dependencies installed
- [ ] pytest and ruff pass
- [ ] Pipeline completes with 6 feature files
- [ ] Training creates registered models
- [ ] API health endpoint returns `"status": "ok"` with both models
- [ ] SHAP, fairness, and drift reports exist
- [ ] Dashboard loads without errors and shows health panel
- [ ] At least one end-to-end prediction works (API → Dashboard)

---

## Summary: Commands by Task

| Task | Command | Output Folder | Key File(s) |
|------|---------|---------------|------------|
| 1. Pipeline | `./.venv/bin/python -m scripts.run_pipeline --skip-download` | `data/processed/`, `data/features/` | `pipeline_summary.json`, `fare_features.parquet`, `demand_features.parquet` |
| 2. Training | `./.venv/bin/python -m scripts.train_models --n-trials 1` | `mlruns/`, `artifacts/` | MLflow models, `fare_shap_summary.png`, `fare.md` |
| 3. API | `./.venv/bin/python -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000` | Served live | `/health`, `/predict/fare`, `/predict/demand` |
| 4. CI/CD | `./scripts/ci_local.ps1` (local) + `buildspec.yml` (cloud) | Console + CloudWatch | Ruff results, pytest results, coverage |
| 5. Drift | `./.venv/bin/python -m scripts.monitoring.demo_drift_report --problem all --mode drift` | `artifacts/drift/` | `demand_drift_metrics.json`, `fare_drift_metrics.json` |
| 6. Responsible AI | `./.venv/bin/python -m scripts.responsible.run_analysis` | `artifacts/responsible/`, `docs/model_cards/` | SHAP PNGs, fairness JSONs, model cards |
| 7. Dashboard | `./.venv/bin/python -m streamlit run dashboard/app.py` | Served live at :8501 | http://127.0.0.1:8501 |
| 8. Golden Path | All above in sequence | See all above | All artifacts verify end-to-end |

