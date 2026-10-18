# CI/CD Workflow & Deployment Status

This document describes the GitHub Actions CI/CD pipeline and how to view deployment status.

## Workflow Overview

The automated CI/CD pipeline runs on every push and pull request, and automatically deploys to AWS ECS when changes are merged to the `main` branch.

### Pipeline Stages

1. **Lint & Test** (runs on all branches)
   - Install Python 3.11 dependencies
   - Run Ruff linter
   - Run pytest with coverage
   - Upload coverage to Codecov

2. **Build & Deploy** (runs only on main branch)
   - Configure AWS credentials via OIDC
   - Login to Amazon ECR
   - Fetch pre-built artifacts from S3
   - Build Docker image
   - Push image to ECR
   - Update ECS service for zero-downtime deployment
   - Wait for deployment to stabilize

3. **Deployment Status**
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

## AWS Secrets Configuration

For the workflow to deploy to AWS, configure these GitHub Secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Create these secrets:

| Secret Name | Value |
|---|---|
| `AWS_REGION` | `us-east-1` (or your region) |
| `AWS_ROLE_TO_ASSUME` | ARN of IAM role for OIDC |
| `ECR_REPOSITORY_URL` | `account-id.dkr.ecr.region.amazonaws.com/repo-name` |
| `ECS_CLUSTER` | Name of your ECS cluster |
| `ECS_SERVICE` | Name of your ECS service |
| `ARTIFACTS_BUCKET` | S3 bucket name for pre-built artifacts |

## Understanding Deployment Flow

### On Pull Request
- ✅ Linting passes
- ✅ Tests pass with coverage
- ❌ Does NOT deploy (protected by `if: github.ref == 'refs/heads/main'`)
- Shows code review checks passed

### On Push to Main
- ✅ Linting passes
- ✅ Tests pass with coverage
- ✅ Docker image built and pushed to ECR
- ✅ ECS service updated with new image
- ✅ Zero-downtime deployment (rolling update)
- ✅ Deployment status reported

## Troubleshooting

### Workflow fails at build stage
- Check Docker credentials in AWS Secrets
- Verify ECR repository exists
- Check Docker build context (Dockerfile path)

### Workflow fails at deployment stage
- Verify ECS cluster and service names are correct
- Check IAM permissions for ECS updates
- Review CloudWatch logs for ECS task failures

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

## Monitoring Deployments

### Real-time Monitoring

```bash
# Watch ECS service status
aws ecs describe-services \
  --cluster <cluster-name> \
  --services <service-name> \
  --region <region>

# Stream CloudWatch logs
aws logs tail /ecs/taxi-forecasting --follow
```

### Rollback Strategy

If deployment issues occur:

```bash
# Revert to previous commit
git revert <commit-hash>
git push origin main  # Triggers new workflow with previous version
```

The pipeline will automatically re-run and deploy the previous stable version.
