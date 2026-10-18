# L7: Call and Package the Prediction API

- **Duration:** 45 to 60 minutes
- **Cloud required:** No
- **Docker required:** Optional; a local Python fallback is provided
- **Outcome:** Valid and invalid API evidence plus a verified container or local runtime.

## Prerequisites

From the repository root, confirm that the project environment and serving
artifacts exist:

```powershell
.\.venv\Scripts\python.exe --version
Test-Path mlflow.db
Test-Path mlruns
Test-Path data\processed\demand_hourly.parquet
```

```bash
.venv/bin/python --version
if [[ -f mlflow.db ]]; then echo True; else echo False; fi
if [[ -d mlruns ]]; then echo True; else echo False; fi
if [[ -f data/processed/demand_hourly.parquet ]]; then echo True; else echo False; fi
```

Path existence alone does not prove that models are registered. In the MLflow
UI, confirm both `taxi-demand-forecaster` and `taxi-fare-predictor` have registered
versions with accessible artifacts. L5's `--no-register` run does not satisfy
this requirement, and L6 may have registered only fare.

If inputs or registered models are missing, complete the pipeline and
model-training steps in [SETUP.md](SETUP.md). For a bounded teaching run that
registers both models, use:

```powershell
.\.venv\Scripts\python.exe -m scripts.train_models --n-trials 1
```

```bash
.venv/bin/python -m scripts.train_models --n-trials 1
```

If you plan to use Route A, create and verify the portable registry required by
the Docker image:

```powershell
.\.venv\Scripts\python.exe scripts\make_mlflow_portable.py `
	--src mlflow.db `
	--dest mlflow.container.db `
	--new-base "file:///app/mlruns"
Test-Path mlflow.container.db   # should return True
```

```bash
.venv/bin/python scripts/make_mlflow_portable.py --src mlflow.db --dest mlflow.container.db --new-base "file:///app/mlruns"
if [[ -f mlflow.container.db ]]; then echo True; else echo False; fi
```

Repeat this command after retraining so the container uses the latest registry.
Route B does not require `mlflow.container.db`.

## Task 1: Predict the Runtime Result

Record the expected health status, one valid prediction result, and the status
code expected from an invalid request before starting the service.

## Task 2: Start the API

Choose one route.

### Route A: Docker Compose

Confirm Docker is available, then build and start the API and MLflow UI. The
default host ports are occupied in this environment, so use 8001 and 5001:

```powershell
docker version
$env:TAXI_API_HOST_PORT = "8001"
$env:MLFLOW_UI_HOST_PORT = "5001"
docker compose -f docker/docker-compose.yml up --build
```

```bash
docker version
export TAXI_API_HOST_PORT=8001
export MLFLOW_UI_HOST_PORT=5001
docker compose -f docker/docker-compose.yml up --build
```

With these overrides, open the API at `http://localhost:8001` and MLflow at
`http://localhost:5001`. Container ports remain `8000` and `5000`.

If `docker version` reports that the command is unavailable, cannot connect to
the Docker daemon, or does not include Compose, skip the second command and use
Route B. Docker is optional for L7; record that you used the local fallback.

Keep this terminal open. With these overrides, the API is at
`http://localhost:8001` and the MLflow UI is at `http://localhost:5001`.

### Route B: Local Python

Use this route when Docker is unavailable:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```

```bash
.venv/bin/python -m uvicorn src.serving.api:app --host 127.0.0.1 --port 8000
```

Keep this terminal open. This route starts the API at `http://localhost:8000`;
it does not start the MLflow UI, which is not required to complete L7.

## Task 3: Verify Health and Documentation

In another terminal:

```powershell
Invoke-RestMethod http://localhost:8001/health
Start-Process http://localhost:8001/docs
```

```bash
curl --fail --silent --show-error http://localhost:8001/health
open http://localhost:8001/docs
```

Record the health response and identify the fare and demand prediction
endpoints in Swagger UI.

## Task 4: Exercise Valid and Invalid Requests

Use the request examples in `docs/API_EXAMPLES.md` to send requests to
`http://localhost:8001` for this Docker run. Replace the examples' default port
8000 with 8001. Route B continues to use port 8000.

1. One valid fare request.
2. One valid demand request.
3. One invalid request with a missing or out-of-range field.

Record the prediction fields from the valid responses. For the invalid request,
record the HTTP status and the validation message without changing server code.

## Task 5: Inspect the Packaging Boundary

Open `docker/Dockerfile` and identify:

- The builder and runtime stages.
- The copied source, model registry, model artifacts, and demand history.
- Port `8000`.
- The Uvicorn startup command.

Then open `docker/docker-compose.yml` and identify:

- The `api` and `mlflow-ui` services and their port mappings.
- The development `mlflow.db`, model-artifact, and data mounts that override
	the corresponding files baked into the image.
- The API `/health` container check.

If you used Route B, inspect these files as packaging evidence but state that
you did not execute the image build, Compose wiring, or container health check.

Explain why Docker packages the API and its dependencies but does not train the
models or prove that the service is deployed to AWS.

## Task 6: Stop the Runtime

For Docker Compose, press `Ctrl+C`, then run:

```powershell
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml ps   # should show no running services
```

```bash
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml ps
```

For local Python, press `Ctrl+C` in the Uvicorn terminal.

## Result Record

### Runtime route and evidence

```text
Route A used Docker Desktop 4.95.0 and Engine 29.8.2. The first startup failed
because host ports 8000 and 5000 were occupied. Port overrides worked: API
8001 -> container 8000; MLflow UI 5001 -> container 5000. Both containers are
running, and the API container is healthy.
```

### Valid response finding

```text
GET /health returned status ok, both models loaded, 744 history hours, and 253
zones. POST /predict/fare returned HTTP 200, predicted_fare 16.38, and
duration_estimated true.
```

### Invalid response finding

```text
POST /predict/fare with an empty JSON object returned HTTP 422. The response
reported missing trip_distance, pu_location_id, do_location_id, and
pickup_datetime fields.
```

### Packaging explanation and limitation

```text

```

## Completion Check

- The expected result was recorded before starting the service.
- Health and Swagger documentation were inspected.
- Valid fare and demand requests returned interpretable responses.
- An invalid request returned an explained validation error.
- Docker was exercised, or its absence and the local fallback were recorded.
- The result distinguishes local packaging from AWS deployment.