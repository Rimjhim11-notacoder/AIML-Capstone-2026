# Model Card — taxi-fare-predictor

_Generated 2026-10-21 11:09 UTC_

## Overview
Predicts the fare amount for a single taxi trip from its distance, zones, passenger count and calendar context (fare prediction).

- **Problem:** fare
- **Best algorithm:** lightgbm
- **Registry name:** `taxi-fare-predictor`
- **Training data window:** 2024-01
- **Training rows:** 4,000

## Test-set performance

| Metric | Test | Validation |
|--------|------|------------|
| RMSE | 2.0164 | 0.1674 |
| MAE | 0.1910 | 0.1032 |
| MAPE | 0.8409 | 0.8384 |
| R2 | 0.9532 | 0.9996 |

## Top feature drivers (mean |SHAP|)

1. `trip_distance` — 4.3474
2. `trip_duration_min` — 2.3399
3. `day_of_week` — 0.0156
4. `PULocationID` — 0.0146
5. `hour_sin` — 0.0142
6. `hour_cos` — 0.0120
7. `DOLocationID` — 0.0111
8. `dow_sin` — 0.0110
9. `hour` — 0.0106
10. `passenger_count` — 0.0076

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

- Trained on a single month of NYC TLC Yellow Taxi data; tariff changes or surge conditions outside the window are not represented.
- Extreme fares are filtered during cleaning, so very long/expensive trips may be under-predicted.
- Tolls, tips and surcharges are not part of the modelled fare amount.
