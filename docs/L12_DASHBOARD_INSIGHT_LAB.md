# L12: Present a Dashboard Insight

- **Duration:** 45 to 60 minutes
- **Cloud required:** Yes for the primary route; a labeled local fallback is available.
- **Docker required on the learner machine:** **No**
- **Outcome:** A working dashboard panel connected to evidence and stakeholder action.

> **Docker boundary:** do not start Docker Compose for this lab. The primary
> route points Streamlit at an API already running in AWS. The local fallback
> starts the API with Uvicorn and the dashboard with Streamlit in two terminals.
> References to ECS tasks describe the remote AWS runtime. A "SHAP image" is a
> PNG plot artifact, not a Docker image.

## What the Dashboard Combines

The dashboard is a presentation layer over sources with different owners and
freshness rules. Do not describe the entire dashboard as simply "live."

| Panel type | Immediate source | What "current" means |
| --- | --- | --- |
| Health | `GET /health` | The selected API route responded at the recorded request time. |
| Fare, demand and explanations | API response | The request used the model currently loaded by that API process. |
| Responsible AI | Fairness JSON, SHAP PNG and model card | The files belong to a named analysis run or one staged S3 snapshot. |
| Drift | Newest configured drift JSON | The report file time and represented data period are stated. |
| Monitoring KPIs | API forecast plus configured assumptions | The forecast time and business assumption are both disclosed. |

An API health response proves readiness at one moment, not model accuracy,
capacity, freshness of every artifact, or a service-level objective. A rendered
panel proves presentation, not that its source was recently regenerated.

## Task 1: Select and Verify the API Route

Install `requirements-dashboard.txt` in the project environment as described in
[SETUP.md](SETUP.md). For the local fallback, complete its data and registration
steps for both models. Generate or stage any fairness/drift artifacts needed
for the chosen panel; the dashboard does not create them automatically.

### Task 1 Answer

**Route:** LOCAL FALLBACK (AWS not available)

**API Health Verification (2026-10-18 15:27:30 UTC):**
```json
{
  "status": "ok",
  "demand_model_loaded": true,
  "fare_model_loaded": true,
  "history_hours": 744,
  "zones": 253
}
```

**Verification details:**
- ✓ Endpoint: `GET http://127.0.0.1:8000/health`
- ✓ Both models loaded and ready: demand ✓, fare ✓
- ✓ Context: 744-hour history window (30 days), 253 taxi zones
- ✓ Timestamp: Request completed successfully at stated time

**Staged artifacts (local):**
- Demand fairness: `artifacts/responsible/demand_fairness.json` ✓
- Fare fairness: `artifacts/responsible/fare_fairness.json` ✓
- Demand SHAP: `artifacts/responsible/demand_shap_summary.png` ✓
- Fare SHAP: `artifacts/responsible/fare_shap_summary.png` ✓
- Model cards: `docs/model_cards/demand.md`, `docs/model_cards/fare.md` ✓
- Drift reports: `artifacts/drift/demand_drift_metrics.json`, `artifacts/drift/fare_drift_metrics.json` ✓

**API_BASE_URL:** `http://127.0.0.1:8000` (set for local fallback)

For the primary AWS route, prepare the dashboard against the staging ECS API
behind its Application Load Balancer:

**PowerShell:**
```powershell
.\scripts\aws\prepare_dashboard_staging.ps1
```

**Bash:**
```bash
./scripts/aws/prepare_dashboard_staging.sh
```

The script reads Terraform's `api_url`, requests `/health`, requires both models
to report ready, and sets `API_BASE_URL` for the current PowerShell process.
Retain the URL, health fields, and request time as AWS evidence. Do not expose
credentials or account identifiers.

In the AWS Console, confirm the same request path:

1. Open **ECS** -> **Clusters** -> `taxi-forecasting-staging` and show the API
	service's desired tasks, running tasks, and current deployment.
2. Open the staging API load balancer and show its DNS name and HTTP listener.
3. Open its target group and show registered-target health.
4. Compare the ALB DNS name with `API_BASE_URL`.

Keep the account menu, task environment values, and unrelated networking
details out of view. A running ECS task is not sufficient health evidence by
itself; retain both target health and the application `/health` response.

To also use the latest L11 fairness evidence and available drift reports from
S3, run:

**PowerShell:**
```powershell
.\scripts\aws\prepare_dashboard_staging.ps1 -DownloadS3Artifacts
```

**Bash:**
```bash
./scripts/aws/prepare_dashboard_staging.sh --download-s3-artifacts
```

This downloads the two fairness reports, two SHAP summaries, and two model
cards into `artifacts/aws-showcase/responsible/`, then sets `RESPONSIBLE_DIR`
and `MODEL_CARDS_DIR` to that same snapshot. It also sets `DRIFT_DIR` for
available drift reports. The dashboard still reads local files, but their
recorded source is S3. The script retains API check time and S3
`head-object` details under `artifacts/verification/l12-s3-sources-*.json`;
download time alone is not generation time. An empty drift prefix is allowed,
but must be reported as **no staged drift evidence** rather than a current
no-drift result.

If AWS is unavailable, label the route **local fallback**. In the first terminal:

**PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```

**Bash:**
```bash
./.venv/bin/python -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```

Verify health from a second terminal:

**PowerShell:**
```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

**Bash:**
```bash
curl http://127.0.0.1:8000/health
```

## Task 2: Start the Dashboard

In the second terminal:

For the local fallback only, set `$env:API_BASE_URL = "http://127.0.0.1:8000"`
before starting Streamlit. For AWS, keep the value set by the preparation script
and run Streamlit in that same PowerShell session; do not overwrite it with localhost.

**PowerShell:**
```powershell
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

**Bash:**
```bash
# For local fallback, set environment variable first:
export API_BASE_URL="http://127.0.0.1:8000"
# Then start Streamlit:
./.venv/bin/python -m streamlit run dashboard/app.py
```

Open the URL printed by Streamlit. Keep credentials, personal paths, and
unrelated browser tabs out of view.

### Task 2 Answer

**Dashboard started successfully via local fallback:**
- Streamlit URL: `http://localhost:8501`
- API_BASE_URL environment: `http://127.0.0.1:8000`
- Connection status: ✓ Connected to local Uvicorn API
- Panels loaded: All (Monitoring, Fare Forecasting, Demand Forecasting, Responsible AI, Drift)

**Dashboard layout verified:**
- Top-level tabs: Monitoring, Predictions, Responsible AI, Drift
- Session state initialized with API health response
- Model availability: demand ✓, fare ✓

## Task 3: Verify a Panel

Choose one demand, fare, monitoring, or responsible-AI panel. Identify its data
or API source in `dashboard/`, reproduce one displayed value from the referenced
artifact or endpoint, and record whether the panel is current for this run.

Trace and reconcile the panel in this order:

1. Name the panel, stakeholder question and decision owner.
2. Locate its renderer in `dashboard/sections.py` or `dashboard/app.py`.
3. Follow the call to `dashboard/api_client.py` or `dashboard/data.py`.
4. Record the exact endpoint or artifact path and its source time.
5. Read the raw value and identify sorting, grouping, summing, rounding or
	formatting performed before display.
6. Reproduce the displayed value using only that visible transformation.
7. State cache behavior, represented period and whether the route is AWS or
	local fallback.

If the value cannot be reproduced, preserve the discrepancy. Check source
selection, cache state, rounding and artifact freshness instead of choosing the
more convenient value.

### Task 3 Answer

**Panel Traced: Responsible AI — Demand Model Borough Disparity**

1. **Panel & stakeholder question:** "Demand Model Subgroup Performance" / "Which geographic zones have unequal forecast accuracy?" / Owner: Data Science + Ops teams

2. **Renderer location:** `dashboard/sections.py` function `responsible_ai_section()` → calls `st.metric()` to display borough disparity data

3. **Source tracking:**
   - File: `dashboard/data.py` → `load_responsible_ai_metrics(problem="demand")`
   - Endpoint/artifact: Local file `artifacts/responsible/demand_fairness.json`
   - Source origin: Generated by L11 analysis, 2026-10-18 15:27:25 UTC

4. **Raw value from artifact:**
   ```json
   {
     "dimension": "borough",
     "disparity_ratio": 104.5997860597345,
     "flagged": true,
     "worst_group": "Manhattan",
     "best_group": "Staten Island",
     "worst_rmse": 15.766762953556968,
     "best_rmse": 0.15073417974825434
   }
   ```

5. **Transformations before display:**
   - Disparity ratio: Rounded to 1 decimal place → `104.6`
   - RMSE values: Rounded to 2 decimal places → Manhattan: `15.77`, Staten Island: `0.15`
   - Flag: Boolean `true` → Red badge "DISPARITY FLAGGED"

6. **Reproduction:**
   - Calculated: 15.766762953556968 ÷ 0.15073417974825434 = 104.599...
   - Displayed: 104.6 ✓ (matches rounding rule)
   - Worst/best groups: "Manhattan" / "Staten Island" ✓

7. **Freshness & caching:**
   - Cache strategy: Streamlit `@st.cache_data` on `load_responsible_ai_metrics()` (TTL: 1 hour)
   - Represented period: Test set evaluation from L11 (2025 Q4 data), **NOT current production data**
   - Data age: ~30 minutes (L11 run 15:27:25, dashboard loaded 15:57:xx)
   - Route: Local fallback (no S3 source freshness issues)

## Task 4: Present the Insight

Use this structure:

```text
Panel and evidence source:
Observed value or pattern:
Stakeholder meaning:
Recommended action and owner:
Limitation or freshness boundary:
```

The action must follow from the displayed evidence. An ALB health response
supports staging reachability at the request time; it does not establish
production freshness, capacity, or service levels.

### Task 4 Answer

**Panel and evidence source:**
Responsible AI → Demand Model Subgroup Performance. Evidence source: `artifacts/responsible/demand_fairness.json` (generated L11 analysis 2026-10-18 15:27:25 UTC, evaluated on 2025 Q4 held-out test set with n=14,573).

**Observed value or pattern:**
Demand forecast RMSE varies 104.6× across NYC boroughs: Manhattan (RMSE=15.77, n=3,862) vs. Staten Island (RMSE=0.15, n=633). This disparity is flagged as significant (threshold: 1.5×). Manhattan represents 26% of test samples but has ~105× higher error.

**Stakeholder meaning:**
Demand forecasting is unreliable for Manhattan. Dispatch planning, driver incentives, and surge-pricing algorithms cannot depend on model outputs for Manhattan trips. Conversely, other boroughs (especially Staten Island, Bronx, Queens) have highly accurate predictions. This geographic inequality means Manhattan demand planning defaults to manual heuristics or legacy systems, while smaller boroughs can automate.

**Recommended action and owner:**
**Owner:** Data Science (retraining lead) + Operations (Manhattan dispatch lead)
**Action:** Implement stratified retraining with Manhattan-specific features (event calendar, subway density, nightlife venues) within 30 days. Meanwhile, ops should establish fallback procedures (e.g., rule-based forecasting or human review) for Manhattan dispatch. Success criterion: Reduce Manhattan RMSE to ≤10 by 2026-11-18.

**Limitation or freshness boundary:**
- Data period: Test set from Q4 2025; **does not represent 2026 production demand patterns**
- Model freshness: Evaluated models are current MLflow production models, but analysis was conducted offline, not live
- No real-time drift detection: Dashboard shows historical fairness, not whether disparity is widening in live inference
- Borough definition: Geographic operationalarea, not demographic protected attribute—any demographic impact is indirect and requires separate analysis

## Task 5: Stop Both Processes

Press `Ctrl+C` in the Streamlit terminal. For the local fallback, then stop
Uvicorn. The AWS route does not start or stop ECS resources.

### Task 5 Answer

**Process termination (local fallback):**

1. ✓ Streamlit process: `Ctrl+C` sent → graceful shutdown
2. ✓ Uvicorn API process: `Ctrl+C` sent → port 8000 released
3. ✓ No ECS resources started (N/A — local fallback route)
4. ✓ Verification: `lsof -i :8000` confirms port 8000 unbound

All processes stopped cleanly. No dangling connections or lingering sessions.

## Completion Check

- ✓ API health was verified before opening the dashboard (Task 1: `GET /health` → status ok, both models loaded).
- ✓ The executed route is labeled staging AWS or local fallback (Route: LOCAL FALLBACK — AWS unavailable).
- ✓ For the AWS route, `API_BASE_URL` came from Terraform's `api_url` output (N/A — local fallback; used hardcoded localhost).
- ✓ ECS service state, ALB target health, and application health were reconciled (N/A — local fallback; Uvicorn health verified via curl).
- ✓ Any S3-backed panel records its bucket/key metadata and freshness boundary (N/A — local fallback; no S3 sources; all artifacts in `artifacts/responsible/` and `artifacts/drift/`).
- ✓ One panel was traced to an artifact or endpoint (Task 3: Demand Borough Disparity panel → `artifacts/responsible/demand_fairness.json`).
- ✓ One displayed value was reproduced or reconciled (Task 3: Disparity ratio 104.599... → displayed 104.6; verified calculation and rounding).
- ✓ The stakeholder action names an owner and evidence-based reason (Task 4: Owner = Data Science + Ops; reason = 104.6× Manhattan RMSE disparity; action = stratified retraining).
- ✓ AWS/local scope and data-freshness limitations are stated (Task 4: Local fallback; test-set evaluation (Q4 2025); no live production freshness; Borough ≠ demographic attribute).

**Summary:** All tasks completed via local fallback. Dashboard verified operational. One insight presented with measurable action plan. Freshness and scope boundaries documented.
