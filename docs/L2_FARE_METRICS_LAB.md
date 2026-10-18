# L2: Guess the Fare and Feel the Metrics

- **Duration:** 45 to 60 minutes
- **Cloud required:** No
- **Outcome:** A plain-language comparison of fare errors using MAE and RMSE.

## Learning Objectives

1. Distinguish an actual fare from a predicted fare.
2. Calculate signed, absolute, and squared errors.
3. Explain why positive and negative errors can cancel.
4. Interpret MAE and RMSE in dollars.
5. Show why RMSE reacts more strongly to one large miss.

## Part A: Commit Fare Guesses

Complete `Your guess` and `Reason` before viewing Part B.

| Trip | Description | Your guess | Reason |
| --- | --- | ---: | --- |
| A | 1.2 miles, weekday morning, Midtown |  |  |
| B | 2.5 miles, weekday afternoon, Manhattan |  |  |
| C | 4 miles, evening, Manhattan to Brooklyn |  |  |
| D | 8 miles, evening airport route |  |  |
| E | 5.5 miles, late evening, Queens |  |  |

## Part B: Calculate the Shared Errors

Use the convention:

```text
Error = prediction - actual
```

| Trip | Actual fare | Shared prediction | Error | Absolute error | Squared error |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | $10 | $12 | $2 | $2 | $4 |
| B | $15 | $13 | -$2 | $2 | $4 |
| C | $20 | $22 | $2 | $2 | $4 |
| D | $30 | $40 | $10 | $10 | $100 |
| E | $25 | $23 | -$2 | $2 | $4 |

Complete these calculations:

```text
Sum of signed errors = $10
Mean signed error = $2

MAE = sum of absolute errors / 5 = $18 / 5 = $3.60

Mean squared error = sum of squared errors / 5 = $116 / 5 = 23.2 dollars squared
RMSE = square root of mean squared error = sqrt(23.2) = $4.82
```

## Part C: Interpret the Baseline

1. What information can the mean signed error hide?
2. What does MAE mean for these five predictions?
3. Why is RMSE larger than MAE here?
4. Which trip contributes most to RMSE, and why?
5. Which operational groups should be checked separately before drawing a
   broad conclusion?

Answers:

1. Positive and negative errors can cancel. Here four errors of $2 in either
   direction partially offset trip D's $10 overprediction, so the mean signed
   error of $2 does not show the size or spread of individual misses.
2. These five predictions are off by an average of $3.60 in absolute fare
   dollars.
3. Squaring gives larger errors more influence. Trip D's $10 miss contributes
   $100 of the total 116 squared dollars, making RMSE ($4.82) greater than MAE
   ($3.60).
4. Trip D contributes most: its squared error is 100, compared with 4 for each
   other trip.
5. Check groups such as airport versus non-airport trips, trip-distance bands,
   pickup and drop-off zones, and time of day or day of week. Compare groups
   only with enough examples; this five-trip exercise is not enough to support
   operational conclusions.

### Verify After Calculating

The recording verifies the hand calculation with the project's metric helpers.
Run this from the repository root after completing the baseline arithmetic:

```powershell
@'
import numpy as np
from src.models.common import mae, rmse

actual = np.array([10, 15, 20, 30, 25], dtype=float)
predicted = np.array([12, 13, 22, 40, 23], dtype=float)
print("MAE:", mae(actual, predicted))
print("RMSE:", rmse(actual, predicted))
'@ | .\.venv\Scripts\python.exe -
```

```bash
.venv/bin/python - <<'PY'
import numpy as np
from src.models.common import mae, rmse

actual = np.array([10, 15, 20, 30, 25], dtype=float)
predicted = np.array([12, 13, 22, 40, 23], dtype=float)
print("MAE:", mae(actual, predicted))
print("RMSE:", rmse(actual, predicted))
PY
```

Compare full precision before rounding to cents. Inspect
[the metric helpers](../src/models/common.py) and
[their tests](../tests/unit/test_models.py). Reversing subtraction changes the
signed error, but not MAE or RMSE after absolute values or squaring.

## Part D: Extreme-Miss Comparison

Change only trip D's prediction from `$40` to `$60`.

| Metric | Baseline | Extreme case | Increase |
| --- | ---: | ---: | ---: |
| MAE | $3.60 | $7.60 | $4.00 |
| RMSE | $4.82 | $13.54 | $8.72 |

Record the changed trip-D values:

```text
Signed error = $30
Absolute error = $30
Squared error = $900
```

After calculating the extreme case, rerun the verification block with only the
fourth prediction changed from `40` to `60`, as in the recording. The actuals
and the other four predictions must stay unchanged.

The extreme-case metrics are MAE `$7.60` and RMSE `$13.54` (full-precision
RMSE: `13.535139452550904`). Relative to baseline, MAE increases by `$4.00`
and RMSE by `$8.72`.

## Exit Ticket

Complete each statement:

1. Mean signed error can mislead because over- and underpredictions can cancel.
2. MAE means the average absolute prediction error; here it is `$3.60` across
   these five example trips.
3. RMSE is larger in the baseline because squaring emphasizes the larger trip-D
   error.
4. MAE and RMSE should be reported with dollar units, sample size, dataset and
   evaluation context, and relevant subgroup checks.

## Completion Check

- All five personal fare guesses are recorded before the shared values appear.
- The shared error table contains signed, absolute, and squared errors.
- MAE and RMSE calculations show the working and retain dollar units.
- Repository code confirms the hand-calculated values.
- The extreme-miss comparison changes only trip D.
- The interpretations state sample size, context, and relevant subgroup checks.