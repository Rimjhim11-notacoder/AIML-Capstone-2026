# Model Card — taxi-demand-forecaster

_Generated 2026-10-18 05:29 UTC_

## Overview
Predicts the number of taxi pickups for a given zone and hour (demand forecasting).

- **Problem:** demand
- **Best algorithm:** xgboost
- **Registry name:** `taxi-demand-forecaster`
- **Training data window:** 2024-01
- **Training rows:** 116,582

## Test-set performance

| Metric | Test | Validation |
|--------|------|------------|
| RMSE | 8.7243 | 8.3490 |
| MAE | 2.5842 | 2.6110 |
| MAPE | 41.9167 | 47.0890 |
| R2 | 0.9706 | 0.9629 |

## Top feature drivers (mean |SHAP|)

1. `lag_1` — 13.7443
2. `lag_168` — 6.2118
3. `lag_24` — 3.6864
4. `hour_cos` — 0.6352
5. `lag_3` — 0.6225
6. `lag_2` — 0.3076
7. `rolling_mean_168` — 0.2640
8. `rolling_std_3` — 0.2603
9. `hour` — 0.2514
10. `rolling_std_168` — 0.2329

## Hyperparameters

```json
{
  "n_estimators": 250,
  "max_depth": 5,
  "learning_rate": 0.06333268775321842,
  "subsample": 0.6563696899899051,
  "colsample_bytree": 0.9208787923016158,
  "min_child_weight": 1,
  "reg_lambda": 8.862326508576253
}
```

## Limitations

- Trained on a single month of NYC TLC Yellow Taxi data; seasonal effects beyond the training window are not captured.
- Lag/rolling features require recent history — cold-start zones/hours are less reliable.
- Only Yellow Taxi pickups are modelled (no green taxi / FHV).
