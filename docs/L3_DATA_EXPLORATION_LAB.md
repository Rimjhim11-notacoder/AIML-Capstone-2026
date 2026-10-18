# L3: Explore the Data and Trace Its Lineage

- **Cloud required:** No; initial source download requires internet.
- **Outcome:** Three findings about cleaning, demand, and feature/split behavior,
  each grounded in the executed notebook or persisted pipeline evidence.
- **Recording companion:** Follow the finalized L3 route below. L4 revisits the
  persistence and consistency checks; it does not replace this exploratory walkthrough.

## 1. Read the Complete Route

Open the [lineage diagram](data-lineage-route.png). Trace source, import,
cleaning, the demand/fare branch, chronological splits, and downstream consumers.
Distinguish transformation arrows from reference/evidence arrows.

Keep the three row meanings explicit:

- Raw trips: one published completed trip.
- Demand: one observed pickup zone during one hour, including inserted zero counts.
- Fare: one accepted completed trip after cleaning, targeting `fare_amount`.

## 2. Verify the Official Source

Open the [NYC TLC Trip Record Data page](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
Identify Yellow Taxi trip Parquet and the taxi-zone lookup CSV. The recording
uses January 2024; this is the configured teaching snapshot, not a claim that it
is the latest publication. Zones are broad labels, not identities or GPS traces.

## 3. Connect Source to Code

Inspect [configuration](../config/config.yaml),
[ingestion](../src/data/ingestion.py), and
[the pipeline entry point](../scripts/run_pipeline.py), in that order. Record
the configured period, source URLs, filenames, and local destinations. Separate
download/load responsibility from validation and feature engineering.

## 4. Run and Open the Notebook

Complete [environment setup](SETUP.md) first. With raw inputs already present,
the recorded persistence command is:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_pipeline --skip-download
```

If a raw file is missing, acquire it using the recorded fallback:

```powershell
.\.venv\Scripts\python.exe -m scripts.run_pipeline
```

Open [the exploration notebook](../notebooks/01_explore_dataset.ipynb) and select
the project `.venv` kernel. The recording preparation also rebuilds this notebook
with `python -m scripts.build_explore_notebook`. That command overwrites the
generated notebook, so use it only when intentionally regenerating it, not after
adding work you need to retain. No rebuild is required merely to open the notebook.

## 5. Execute the Notebook in Order

Run one code cell at a time and interpret its output before continuing. Follow
the recorded sequence, using section names if cell positions have changed:

| Notebook segment | Evidence to inspect |
| --- | --- |
| Setup and source inventory | Project root, interpreter, provider, files, and source period |
| Raw inputs and schema | Trip preview, required fields, types, and zone lookup |
| Cleaning | Unsuitable values, ordered rules, retained/removed counts and reasons |
| Demand aggregation | Unique zone-hour keys, dense dimensions, zero rows, hourly profile, busiest zones |
| Demand features | Calendar inputs, past-only lags/rolling statistics, and history warm-up |
| Fare features | One clean trip per row, distance/duration/passengers/zones/calendar, and fare-distance plot |
| Chronological splits | All six train/validation/test outputs and their time boundaries |
| Artifacts and lineage checks | Saved paths, row-count relationships, unique keys, and assertions |

The notebook calculates stages in memory to explain them. The pipeline writes
the official persisted outputs. Do not claim a saved file was refreshed merely
because its in-memory equivalent was recalculated.

## 6. Reconcile Persisted Evidence

Check the two raw inputs, clean trips, hourly demand, pipeline summary, both
complete feature tables, and all six split files: thirteen expected artifacts
in the recorded route. File existence proves persistence, not correctness.

Run the notebook's final assertions. Confirm cleaning did not add trips, fare
rows match clean rows, demand zone-hour keys are unique, and split times move
forward. Inspect the lag/rolling code separately to establish past-only inputs.

## 7. Present Three Findings

Use current outputs, not memorized recording values:

1. **Cleaning:** raw, retained, and removed row counts; largest removal reason.
2. **Demand:** zones, hours, zone-hour rows, zero-count rows, and busiest zone.
3. **Features and splits:** fare row preservation, demand history warm-up, and
   chronological split boundaries.

For each finding record the notebook output or artifact, its configured period,
what it supports, and one limit. Counts can differ when input data or configuration
changes; preserve and investigate the difference instead of forcing a match.

## Observed Answers: January 2024 Artifacts

These figures come from persisted January 2024 artifacts. Notebook execution was
verified: all code cells ran in order, and the final cell printed
`All lineage checks passed.`

### Source and Configuration

- Period: January 2024 Yellow Taxi data.
- Trips: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet`, saved under `data/raw/`.
- Zone lookup: `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv`, saved under `data/raw/`.
- The lookup lists 265 zones. Demand uses 253 pickup zones.
- Ingestion downloads and loads files. Later stages validate, clean, aggregate,
  engineer features, and split the data.

### Finding 1: Cleaning

Evidence: `data/processed/pipeline_summary.json` and `trips_clean.parquet`.

- Raw: 2,964,624 trips across 19 columns. Retained: 2,727,349. Removed: 237,275.
- Passenger count has 140,162 nulls. The cleaner treats null as zero.
- The largest removal reason was passenger count out of range: 167,879 trips.
- Other removals: duration 36,999; fare 32,321; distance 58; period 18.
- Raw fares ranged from -$899 to $5,000. The configured fare range is $0 to $500.
- These counts reflect project filters. They do not prove every removed trip was
  invalid.

### Finding 2: Demand

Evidence: `data/processed/demand_hourly.parquet` and the zone lookup.

- Coverage: 253 zones over 744 hours. The table has 188,232 unique zone-hour rows.
- It contains 118,510 zero-count rows.
- Zone 132 (JFK Airport, Queens) was busiest, with 135,950 pickups.
- Upper East Side South was next with 135,538 pickups. Midtown Center had 135,068.
- Hour 18:00 had the highest monthly total: 196,249 pickups.
- Zero rows may be inserted. A row represents a zone-hour, not one trip.
- This is one month of Yellow Taxi data using broad TLC zones.

### Finding 3: Features and Splits

Evidence: the fare and demand feature tables and their six split files under
`data/features/`.

- Fare features preserve all 2,727,349 clean trips and have 16 columns. The
  sample plot shows fares generally rise with distance, but distance alone does
  not explain the spread or outliers.
- Demand features have 145,728 rows and start January 8 at 00:00. The 168-hour
- Demand features have 145,728 rows and 23 columns. They start January 8 at
  00:00 after a 168-hour warm-up removes 42,504 zone-hour rows. Lags are 1, 2,
  3, 24, and 168 hours; rolling windows are 3, 24, and 168 hours.
- Fare splits: train 2,181,879 (Jan 1 00:00 to Jan 26 06:29:51); validation
  272,735 (Jan 26 06:29:55 to Jan 28 22:20:01); test 272,735 (Jan 28 22:20:03
  to Jan 31 23:59:55).
- Demand splits: train 116,582 (Jan 8 00:00 to Jan 27 04:00); validation
  14,573 (Jan 27 04:00 to Jan 29 14:00); test 14,573 (Jan 29 14:00 to Jan 31
  23:00).
- Demand rows share boundary timestamps across neighboring splits. The split
  helper sorts and slices by row count, so the partitions are not strictly
  timestamp-disjoint.
- One month of data cannot establish performance on future months.
- All 13 expected artifact paths existed. Final checks confirmed fare row
  preservation, unique zone-hour keys, and nondecreasing split times.
- One month cannot establish performance on future months.



## Completion Check

- Source and configuration are identified before interpreting results.
- All notebook sections were executed or a specific failed/skipped step is recorded.
- The three row meanings and the two feature branches remain distinct.
- Pipeline outputs and notebook calculations were reconciled.
- Three findings cite observed evidence.
- Limitations cover one-month Yellow Taxi scope, broad geography, no direct
  demographic attributes, project cleaning assumptions, and no currentness guarantee.