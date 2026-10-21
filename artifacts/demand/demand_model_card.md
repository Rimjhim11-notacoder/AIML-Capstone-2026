# Model Card — taxi-demand-forecaster

_Generated 2026-10-21 11:09 UTC_

## Overview
Predicts the number of taxi pickups for a given zone and hour (demand forecasting).

- **Problem:** demand
- **Best algorithm:** lightgbm
- **Registry name:** `taxi-demand-forecaster`
- **Training data window:** 2024-01
- **Training rows:** 1,075

## Test-set performance

| Metric | Test | Validation |
|--------|------|------------|
| RMSE | 1.5393 | 1.5144 |
| MAE | 1.2426 | 1.1897 |
| MAPE | 53.3719 | 50.7175 |
| R2 | -0.1274 | -0.1165 |

## Top feature drivers (mean |SHAP|)

1. `rolling_std_168` — 0.1680
2. `rolling_std_3` — 0.1514
3. `rolling_std_24` — 0.1453
4. `rolling_mean_168` — 0.1378
5. `lag_1` — 0.1072
6. `rolling_mean_24` — 0.1016
7. `lag_168` — 0.0974
8. `hour_cos` — 0.0790
9. `lag_24` — 0.0729
10. `hour_sin` — 0.0721

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
  "reg_lambda": 2.915443189153755
}
```

## Limitations

- Trained on a single month of NYC TLC Yellow Taxi data; seasonal effects beyond the training window are not captured.
- Lag/rolling features require recent history — cold-start zones/hours are less reliable.
- Only Yellow Taxi pickups are modelled (no green taxi / FHV).
