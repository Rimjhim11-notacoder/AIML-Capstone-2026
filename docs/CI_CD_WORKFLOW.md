# CI/CD Workflow & Build Status

This document describes the GitHub Actions CI/CD pipeline and how to view build status.

## Workflow Overview

The automated CI/CD pipeline runs on every push and pull request. When changes are merged to the `main` branch, it builds and smoke-tests the Docker image locally on the GitHub Actions runner.

### Pipeline Stages

1. **Lint & Test** (runs on all branches)
   - Install Python 3.11 dependencies
   - Run Ruff linter
   - Run pytest with coverage
   - Upload coverage to Codecov

2. **Build & Run (Local Docker)** (runs only on main branch)
   - Generate synthetic fixture data (using the same TLC schema as real data)
   - Run the full pipeline against the fixture data
   - Train models with reduced hyperparameter tuning (--n-trials 2 for speed)
   - Build the Docker image locally
   - Start the API container on the runner
   - Smoke test the /health endpoint to verify the service starts correctly
   - Clean up containers

3. **Build Status**
   - Report final status to GitHub Actions

## Viewing Workflow Runs

### Via GitHub Web Interface

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. Select **CI/CD Pipeline** from the workflow list
4. Click on any run to see:
   - Overall status (✅ Success or ❌ Failed)
   - Duration of each job
   - Logs from each step
   - Artifacts uploaded (coverage reports)

### Command Line (gh CLI)

```bash
# List recent workflow runs
gh run list --workflow=ci-cd.yml

# View specific run details
gh run view <run-id>

# Watch a run in real-time
gh run watch <run-id>

# View logs for a specific job
gh run view <run-id> --log
```

## Deployment Status Badges

Add these badges to your README to display pipeline status:

```markdown
[![CI/CD Pipeline](https://github.com/yourusername/repo/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yourusername/repo/actions/workflows/ci-cd.yml)
[![codecov](https://codecov.io/gh/yourusername/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/repo)
```

These badges show:
- **Pipeline Badge**: Green (✅) when main passes, red (❌) when failed
- **Coverage Badge**: Test coverage percentage on main branch

## Secrets Configuration

No AWS secrets are required. The workflow uses Docker Compose to build and test the image locally on the GitHub Actions runner.

## Understanding Build Flow

### On Pull Request
- ✅ Linting passes
- ✅ Tests pass with coverage
- ❌ Does NOT build image (protected by `if: github.ref == 'refs/heads/main'`)
- Shows code review checks passed

### On Push to Main
- ✅ Linting passes
- ✅ Tests pass with coverage
- ✅ Fixture data generated and models trained locally
- ✅ Docker image built locally
- ✅ API container started on the runner
- ✅ /health endpoint verified (smoke test)
- ✅ Containers cleaned up
- ✅ Build status reported

## Troubleshooting

### Workflow fails at fixture generation or training stage
- Verify `requirements.txt` has all needed dependencies
- Check `tests/synthetic.py` exists and is importable
- Run locally: `python -m scripts.generate_ci_fixture_data`

### Workflow fails at Docker build stage
- Check Docker build context and Dockerfile path
- Run locally: `docker compose -f docker/docker-compose.yml build api`
- Review Docker layer caching and dependencies

### Workflow fails at health check (smoke test)
- The /health endpoint may take a moment to become ready; retries are built in
- Check `docker compose logs api` (logs are dumped on failure)
- Verify the API image exposes port 8000: `docker inspect <image> | grep ExposedPorts`
- Run locally: `docker compose -f docker/docker-compose.yml up api` and curl `/health`

### Tests fail locally but pass in CI
- Ensure Python version is 3.11+
- Check dependencies in requirements.txt
- Run: `pip install -r requirements.txt && pytest`

## Local CI Testing

Before pushing, test the pipeline locally:

```bash
# Run linting
ruff check .

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Build Docker image (optional)
docker build -f docker/Dockerfile -t taxi-forecasting:test .
```

## Local Testing

Before pushing to main, test the build locally using the same steps as CI:

```bash
# Generate fixture data
python -m scripts.generate_ci_fixture_data

# Run the pipeline
python -m scripts.run_pipeline --skip-download

# Train models with reduced trials
python -m scripts.train_models --n-trials 2

# Make MLflow portable for Docker
python scripts/make_mlflow_portable.py --src mlflow.db --dest mlflow.container.db --new-base file:///app/mlruns

# Build and test the Docker image
docker compose -f docker/docker-compose.yml up --build -d api

# Test the health endpoint
curl -s http://localhost:8000/health | python -m json.tool

# Clean up
docker compose -f docker/docker-compose.yml down -v
```

### Rollback Strategy

If a build fails on main:

```bash
# Revert the problematic commit
git revert <commit-hash>
git push origin main  # Triggers new workflow with previous version
```

The pipeline will automatically re-run with the previous stable version. Since we're not deploying to a persistent service, there's no need for a complex rollback — just pushing to main triggers a new build.
