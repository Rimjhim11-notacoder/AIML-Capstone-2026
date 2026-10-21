# Model Card — taxi-fare-predictor

_Generated 2026-10-18 05:37 UTC_

## Overview
Predicts the fare amount for a single taxi trip from its distance, zones, passenger count and calendar context (fare prediction).

- **Problem:** fare
- **Best algorithm:** lightgbm
- **Registry name:** `taxi-fare-predictor`
- **Training data window:** 2024-01
- **Training rows:** 2,181,879

## Test-set performance

| Metric | Test | Validation |
|--------|------|------------|
| RMSE | 3.4378 | 3.3531 |
| MAE | 0.8011 | 0.7550 |
| MAPE | 8.9865 | 15.0875 |
| R2 | 0.9559 | 0.9559 |

## Top feature drivers (mean |SHAP|)

1. `trip_distance` — 8.5591
2. `trip_duration_min` — 3.5429
3. `DOLocationID` — 0.4671
4. `PULocationID` — 0.2319
5. `passenger_count` — 0.1100
6. `hour_cos` — 0.0522
7. `hour` — 0.0317
8. `hour_sin` — 0.0314
9. `day_of_week` — 0.0147
10. `dow_sin` — 0.0134

## Hyperparameters

```json
{
  "n_estimators": 400,
  "num_leaves": 59,
  "max_depth": 12,
  "learning_rate": 0.13962563737015762,
  "subsample": 0.9757995766256756,
  "colsample_bytree": 0.9579309401710595,
  "min_child_samples": 62,
  "reg_lambda": 4.869640941520899
}
```

## Limitations

- Trained on a single month of NYC TLC Yellow Taxi data; tariff changes or surge conditions outside the window are not represented.
- Extreme fares are filtered during cleaning, so very long/expensive trips may be under-predicted.
- Tolls, tips and surcharges are not part of the modelled fare amount.
