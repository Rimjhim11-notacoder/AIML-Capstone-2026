# Model Card — taxi-demand-forecaster

_Generated: 2026-10-18 10:00 UTC_

## Model details

- **Problem:** demand
- **Algorithm:** XGBRegressor
- **Target:** `pickup_count`
- **Registry version:** n/a

## Intended use

Operational forecasting of pickup_count to support fleet positioning and rider fare estimates. Not intended for individual pricing decisions or any use with legal/financial consequences for individuals.

## Evaluation — overall (test split)

| Metric | Value |
|--------|-------|
| rmse | 8.7243 |
| mae | 2.5842 |
| mape | 41.9167 |
| r2 | 0.9706 |

## Evaluation — subgroup fairness

### By borough

Disparity ratio (worst/best RMSE): **104.60** (threshold 1.5) — ⚠️ **flagged**. Worst: `Manhattan`, best: `Staten Island`.

| Group | n | RMSE | MAE | MAPE |
|-------|---|------|-----|------|
| Manhattan | 3862 | 15.767 | 7.828 | 30.44 |
| Queens | 3971 | 6.051 | 1.206 | 55.54 |
| Unknown | 116 | 3.284 | 1.984 | 48.79 |
| Brooklyn | 3457 | 0.757 | 0.459 | 57.63 |
| Bronx | 2476 | 0.458 | 0.293 | 67.16 |
| EWR | 58 | 0.290 | 0.176 | 90.93 |
| Staten Island | 633 | 0.151 | 0.135 | 76.39 |

### By time_of_day

Disparity ratio (worst/best RMSE): **2.60** (threshold 1.5) — ⚠️ **flagged**. Worst: `evening`, best: `overnight`.

| Group | n | RMSE | MAE | MAPE |
|-------|---|------|-----|------|
| evening | 4554 | 11.929 | 3.392 | 37.26 |
| afternoon | 3947 | 8.413 | 3.015 | 37.54 |
| morning | 3036 | 6.231 | 2.405 | 41.80 |
| overnight | 3036 | 4.589 | 0.991 | 61.81 |

### By day_type

Disparity ratio (worst/best RMSE): **1.00** (threshold 1.5) — ok. Worst: `weekday`, best: `weekday`.

| Group | n | RMSE | MAE | MAPE |
|-------|---|------|-----|------|
| weekday | 14573 | 8.724 | 2.584 | 41.92 |

### By holiday

Disparity ratio (worst/best RMSE): **1.00** (threshold 1.5) — ok. Worst: `non-holiday`, best: `non-holiday`.

| Group | n | RMSE | MAE | MAPE |
|-------|---|------|-----|------|
| non-holiday | 14573 | 8.724 | 2.584 | 41.92 |

### By airport

Disparity ratio (worst/best RMSE): **4.25** (threshold 1.5) — ⚠️ **flagged**. Worst: `airport`, best: `non-airport`.

| Group | n | RMSE | MAE | MAPE |
|-------|---|------|-----|------|
| airport | 116 | 34.790 | 25.518 | 35.65 |
| non-airport | 14457 | 8.186 | 2.400 | 42.05 |

## Top features (SHAP)

| Feature | Mean |SHAP| |
|---------|-----------|
| lag_1 | 15.0364 |
| lag_168 | 6.8050 |
| lag_24 | 3.7010 |
| lag_3 | 0.6361 |
| hour_cos | 0.6300 |
| lag_2 | 0.3357 |
| rolling_mean_168 | 0.2745 |
| hour_sin | 0.2576 |
| rolling_std_3 | 0.2524 |
| rolling_std_24 | 0.2487 |

## Limitations

- Trained on a single month of NYC Yellow Taxi data; may not generalise to other periods, boroughs served sparsely, or green/for-hire vehicles.
- Predictions degrade under distribution shift (see drift monitoring).

## Ethical considerations

- No demographic or protected attributes are used or available; fairness is assessed as geographic/temporal service equity, not demographic parity.
- Large borough-level disparities could translate into unequal service quality across neighbourhoods and should be monitored.
