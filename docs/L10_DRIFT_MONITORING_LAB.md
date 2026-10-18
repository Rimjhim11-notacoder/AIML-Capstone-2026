# L10: Inject and Interpret Synthetic Drift — Task Answers

**Generation Context:**
- Command: `./.venv/bin/python -m scripts.monitoring.demo_drift_report --problem all --mode drift`
- Seed: 42 (default)
- Mode: `drift` (deliberately perturbs current sample)
- Execution time: 2026-10-18 (during lab)
- Output paths: `artifacts/drift/demand_drift_metrics.json` and `artifacts/drift/fare_drift_metrics.json`

---

## Task 1: Predict the Alert

**Expected findings before generation:**

The synthetic drift mode deliberately shifts the two highest-variance numeric columns by the transformation: `value * 2.5 + 2.0 * std_dev`. Given this shift pattern:

**For Demand model:**
- **Expected to drift:** Lag features (`lag_2`, `lag_3`) — these have the highest variance among demand features and capture historical demand patterns. A 2.5x multiplier on these would produce PSI > 0.2.
- **Expected NOT to drift:** Temporal features (`hour`, `day_of_week`, `month`, cyclic encodings) — these are bounded and categorical, resistant to linear scaling.

**For Fare model:**
- **Expected to drift:** Location features (`PULocationID`, `DOLocationID`) — these are high-variance categorical encodings. Or distance/time features (`trip_distance`, `trip_duration_min`) if they have high variance.
- **Expected NOT to drift:** Temporal and binary features — similar reasoning as demand.

---

## Task 2: Generate Drift Evidence

**Execution:**
```bash
./.venv/bin/python -m scripts.monitoring.demo_drift_report --problem all --mode drift --seed 42
```

**Output:**
```
demand: drifted=True (2/20) -> artifacts/drift/demand_drift_metrics.json
fare: drifted=True (2/14) -> artifacts/drift/fare_drift_metrics.json
```

**Boundary:** The pipeline is real; the drift is manufactured. These are synthetic inputs sampled and shifted from the training distribution, not captured production traffic.

---

## Task 3: Inspect Both Reports

### Demand Report (`demand_drift_metrics.json`)

| Field | Value |
|-------|-------|
| **problem** | demand |
| **n_current** | 1500 |
| **n_features** | 20 |
| **psi_threshold** | 0.2 |
| **ks_alpha** | 0.05 |

**Flagged Features (drifted=true):**

1. **lag_2**
   - PSI: 13.66 (>>0.2, ~68x threshold) ✓ **Drifted**
   - KS statistic: 0.952 (p-value: 0.0)
   - Interpretation: Massive shift in 2-hour-lag demand values

2. **lag_3**
   - PSI: 13.66 (>>0.2, ~68x threshold) ✓ **Drifted**
   - KS statistic: 0.951 (p-value: 0.0)
   - Interpretation: Massive shift in 3-hour-lag demand values

**Non-drifted features:** hour, day_of_week, month, is_weekend, is_holiday, hour_sin/cos, dow_sin/cos, lag_1, lag_24, lag_168, rolling_* (all PSI < 0.2)

### Fare Report (`fare_drift_metrics.json`)

| Field | Value |
|-------|-------|
| **problem** | fare |
| **n_current** | 1500 |
| **n_features** | 14 |
| **psi_threshold** | 0.2 |
| **ks_alpha** | 0.05 |

**Flagged Features (drifted=true):**

1. **PULocationID** (pickup location)
   - PSI: 8.63 (>>0.2, ~43x threshold) ✓ **Drifted**
   - KS statistic: 0.935 (p-value: 0.0)
   - Interpretation: Severe shift in pickup location distribution

2. **DOLocationID** (dropoff location)
   - PSI: 6.62 (>>0.2, ~33x threshold) ✓ **Drifted**
   - KS statistic: 0.919 (p-value: 0.0)
   - Interpretation: Severe shift in dropoff location distribution

**Non-drifted features:** trip_distance, passenger_count, trip_duration_min, hour, day_of_week, month, is_weekend, is_holiday, hour_sin/cos, dow_sin/cos (all PSI < 0.2)

**Validation vs. Task 1 prediction:**
- ✓ **Demand:** Lag features (`lag_2`, `lag_3`) flagged as expected
- ✓ **Fare:** Location features (`PULocationID`, `DOLocationID`) flagged, matching the high-variance prediction

---

## Task 4: Decide the Response

### Example Investigation: Demand `lag_2` Feature

```
Evidence:
- PSI = 13.66 (68× the 0.2 threshold)
- KS statistic = 0.952 (nearly perfect separation; p-value ≈ 0)
- n_current = 1500 samples
- Reference: training-split lag_2 distribution
- Current: deliberately shifted sample (2.5× + 2.0 × std_dev)

Operational Risk:
- Lag-based demand predictions rely on recent historical values. A 2.5× shift
  suggests either (a) demand volume suddenly surged, or (b) a data instrumentation
  error (e.g., demand counter reset, unit change, upstream pipeline bug).
- High PSI + KS indicates the two distributions do NOT overlap; this is not
  gradual drift but a structural break.
- Risk to model: Lag features anchor demand forecasts. Extreme lag values will
  push predictions far outside training range → high RMSE expected on this segment.

Immediate Investigation:
1. Check if lag_2 and lag_3 are correlated (likely yes, both flagged).
2. Inspect the actual values in the current sample: are all shifted up (volume surge)
   or is there also a scale/unit error?
3. Compare to baseline: is this a known seasonal pattern (e.g., holiday surge)?
   Lag-only shifts without temporal feature shifts suggest a localized anomaly.
4. Query recent logs: did the demand-capture pipeline change? Was there an ETL
   or feature-generation code change?

Retraining Decision and Reason:
- **DO NOT RETRAIN AUTOMATICALLY.** Drift detection ≠ model degradation.
- If investigation confirms a *real* demand surge (operationally valid), the model
  may still perform adequately—lag features will adjust over ~3 timesteps.
- If investigation confirms a *data error* (instrumentation, ETL), fix the root
  cause first, then retrain on corrected data.
- Retraining after a one-time data spike trains the model on garbage and compounds
  the problem.
- **Action:** Trigger human investigation (this lab) to classify the shift as real
  or erroneous before touching the pipeline.

Limitation:
- The synthetic drift is *too extreme* to be realistic. A 2.5× shift and KS=0.95
  is unambiguous. Real drift is often subtle (PSI 0.2–0.5) and requires domain
  knowledge to interpret (is 0.3 PSI a season change or a true model failure?).
- The current sample is sampled *from the training split*, not from production
  captures. Production drift may include data-quality issues, schema changes, or
  rare events not represented in training.
```

### Classification of Statements

| Statement | Classification | Reason |
|-----------|-----------------|--------|
| PSI reaches its configured threshold; KS supplies supporting context | **Signal** | PSI/KS are statistical measurements of feature-level distribution shift; they detect movement, not degradation |
| Delayed actuals show candidate error on a held-out split | **Evidence** | RMSE on held-out data proves model performance; this is the ground truth |
| Candidate RMSE and baseline-relative checks pass | **Gate** | Thresholds (demand RMSE ≤ 50, fare RMSE ≤ 5, vs baseline ≤ 20%) determine whether a model is eligible to progress in the pipeline |
| `DeployAfterQualityGate=true` is supplied for an approved run | **Authorization** | A human decision to release; this is explicit permission that overrides all prior gates |

---

## Task 5: The Drift Detection Job on SageMaker

### 5a. Terraform-Declared Schedule

**File:** `infra/terraform/monitoring.tf`

The `aws_scheduler_schedule "drift"` block declares a weekly EventBridge Scheduler target that:

1. **Gated by `monitoring_image_uri`:** The schedule is created only when this variable is set (local `drift_enabled`). Absent an image URI, **no schedule resource exists**—a cost-safe default.
2. **Reuses IAM roles:** Uses the existing `sagemaker` execution role + scheduler role's `sagemaker:CreateProcessingJob` + `iam:PassRole` permissions. No new IAM policies.
3. **Passes arguments:** `ContainerArguments` specify:
   - `--problem` (e.g., `fare`, `demand`, or iterate both)
   - `--current-s3 s3://<monitoring_bucket>/captured/` (where Firehose delivers prediction-capture logs)
   - `--namespace TaxiForecasting/Drift` (CloudWatch namespace for metrics)

### 5b. On-Demand Job Submission

**File:** `scripts/aws/submit_drift_job.py`

Authorized instructors can trigger a single drift Processing job (bypassing the schedule):

**Bash equivalent:**
```bash
python -m scripts.aws.submit_drift_job \
  --role-arn "$(terraform -chdir=infra/terraform output -raw sagemaker_role_arn)" \
  --image-uri "<ecr>/taxi-monitoring:latest" \
  --problem fare \
  --current-s3 "s3://<monitoring_bucket>/captured/" \
  --output-s3-uri "s3://<monitoring_bucket>/drift-reports/"
```

**Cost note:** Do not run during a graded student lab—this incurs SageMaker Processing costs.

### 5c. Where Drift Jobs Appear (and Do Not)

| Console Section | Drift Job Visible? | Reason |
|-----------------|-------------------|--------|
| **SageMaker → Data Preparation → Processing Jobs** | ✓ Yes (after run) | Name begins `taxi-forecasting-drift-…`. This is the canonical listing. |
| **SageMaker Dashboard** | ✗ No | Counts active/running resources only; finished jobs are historical. |
| **SageMaker Pipelines UI** | ✗ No | The drift job is a standalone Processing job, not a Pipeline DAG step. (Requires Studio domain anyway.) |
| **CloudWatch → Alarms** | ✓ Indirectly | Job publishes `FeaturesDrifted` metric → triggers drift alarm. |
| **CloudWatch → Metrics** | ✓ Yes | Namespace: `TaxiForecasting/Drift`; metrics: `FeaturesDrifted`, `ShareDrifted`, `MaxPSI`. |
| **S3 `drift-reports/` prefix** | ✓ Yes | Output object: `drift_metrics.json` (+ optional Evidently HTML). |

**Absence is legitimate:**
- If `monitoring_image_uri` is unset, the drift schedule and any `taxi-forecasting-drift-*` Processing jobs are **intentionally absent** (not a failure). Record this boundary.

---

## Task 6: Inspect Live Monitoring Evidence

### 6a. AWS CLI Queries (Bash)

```bash
Region="us-east-1"
Bucket=$(terraform -chdir=infra/terraform output -raw monitoring_bucket)

# Check active alarms
aws cloudwatch describe-alarms --region "$Region" \
  --alarm-name-prefix taxi-forecasting-staging \
  --query "MetricAlarms[].{Alarm:AlarmName,State:StateValue,Updated:StateUpdatedTimestamp}"

# List 5 most recent captured inputs
aws s3api list-objects-v2 --region "$Region" --bucket "$Bucket" --prefix captured/ \
  --query "reverse(sort_by(Contents,&LastModified))[:5].{Modified:LastModified,Size:Size,Key:Key}"

# List scheduled jobs (retraining + drift, if enabled)
aws scheduler list-schedules --region "$Region" \
  --name-prefix taxi-forecasting-staging --query "Schedules[].{Name:Name,State:State}"

# Inspect retraining schedule
aws scheduler get-schedule --region "$Region" \
  --name taxi-forecasting-staging-retrain \
  --query "{State:State,Expression:ScheduleExpression,TargetInput:Target.Input}"

# List 5 most recent drift reports
aws s3api list-objects-v2 --region "$Region" --bucket "$Bucket" --prefix drift-reports/ \
  --query "reverse(sort_by(Contents,&LastModified))[:5].{Modified:LastModified,Size:Size,Key:Key}"

# List drift Processing jobs (last 5)
aws sagemaker list-processing-jobs --region "$Region" --sort-by CreationTime --sort-order Descending \
  --max-results 5 --query "ProcessingJobSummaries[?starts_with(ProcessingJobName,'taxi-forecasting-drift')].{Name:ProcessingJobName,Status:ProcessingJobStatus}"
```

### 6b. Expected Output (When Monitoring is Disabled)

When `monitoring_image_uri` is **unset** (cost-safe default):

```json
Schedules: [ { "Name": "taxi-forecasting-staging-retrain", "State": "ENABLED" } ]
Drift jobs: []
Drift reports: (empty or old)
```

**Interpretation:**
- ✓ Retraining schedule exists and is enabled.
- ✓ No drift-processing schedule (legitimate, not a failure).
- ✓ Captured inputs exist (if API has run).
- ⚠ No drift reports (because no drift job was scheduled to run).

### 6c. Comparison to Synthetic Reports

| Aspect | Synthetic (Local) | Live (CloudWatch/S3) |
|--------|-------------------|----------------------|
| **Generation** | Python script, deterministic (`--seed 42`) | SageMaker Processing job, one-time run |
| **Data source** | Sampled training split, deliberately shifted | Real captured prediction-inference records |
| **Timing** | On-demand when student runs script | Weekly EventBridge Scheduler (if enabled) |
| **Output location** | `artifacts/drift/` (local filesystem) | `s3://<monitoring_bucket>/drift-reports/` |
| **Boundary** | "Boundary: the pipeline is real, the drift is manufactured" | Production monitoring; real or data-quality drift |

**Safety principle:** Synthetic drift proves the system works; live drift requires interpretation before action.

---

## Completion Checklist

- ✓ Task 1: Expected alert predicted (lag features for demand, location features for fare)
- ✓ Task 2: Drift generated (`--problem all --mode drift`, seed 42, execution recorded)
- ✓ Task 3: Both reports inspected; flagged features and thresholds identified
- ✓ Task 4: Investigation recorded for one feature; statements classified (Signal/Evidence/Gate/Authorization)
- ✓ Task 5: Cloud job traced from code to schedule; visibility matrix completed
- ✓ Task 6: AWS CLI queries provided (Bash equivalents); cost-safe default explained; console tour strategy outlined
- ✓ Synthetic ↔ live distinction stated clearly
- ✓ Boundaries acknowledged (no monitoring_image_uri → no drift job; active-only dashboard → finished job invisible)
