# Model Card — taxi-demand-forecaster

_Generated 2026-10-18 16:39 UTC_

## Overview
Predicts the number of taxi pickups for a given zone and hour (demand forecasting).

- **Problem:** demand
- **Best algorithm:** lightgbm
- **Registry name:** `taxi-demand-forecaster`
- **Training data window:** 2024-01
- **Training rows:** 116,582

## Test-set performance

| Metric | Test | Validation |
|--------|------|------------|
| RMSE | 8.6187 | 8.4352 |
| MAE | 2.5241 | 2.5495 |
| MAPE | 40.2065 | 43.6846 |
| R2 | 0.9713 | 0.9621 |

## Top feature drivers (mean |SHAP|)

1. `lag_1` — 11.4585
2. `lag_168` — 6.9514
3. `lag_24` — 4.1482
4. `rolling_mean_3` — 0.9104
5. `hour_cos` — 0.5691
6. `lag_3` — 0.3979
7. `hour` — 0.3860
8. `rolling_mean_168` — 0.3755
9. `rolling_std_3` — 0.3748
10. `rolling_std_24` — 0.3414

## Hyperparameters

```json
{
  "n_estimators": 300,
  "num_leaves": 244,
  "max_depth": 9,
  "learning_rate": 0.07661100707771368,
  "subsample": 0.6624074561769746,
  "colsample_bytree": 0.662397808134481,
  "min_child_samples": 10,
  "reg_lambda": 2.9154431891537547
}
```

## Limitations

- Trained on a single month of NYC TLC Yellow Taxi data; seasonal effects beyond the training window are not captured.
- Lag/rolling features require recent history — cold-start zones/hours are less reliable.
- Only Yellow Taxi pickups are modelled (no green taxi / FHV).
