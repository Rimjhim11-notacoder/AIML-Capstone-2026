"""Generate synthetic NYC TLC fixture data for CI builds.

Produces a minimal dataset using the same schema as real yellow taxi data, so
the pipeline and models can be trained quickly in CI without downloading real
data or performing a long hyperparameter search.

Usage::

    python -m scripts.generate_ci_fixture_data
"""

from __future__ import annotations

import logging

import pandas as pd

from src.config import get_config
from src.data.ingestion import trip_filename
from tests.synthetic import make_synthetic_trips

logger = logging.getLogger(__name__)


def main() -> None:
    config = get_config()
    config.ensure_dirs()

    # Generate synthetic trips matching TLC schema
    logger.info("Generating synthetic trips data for CI fixture...")
    trips_df = make_synthetic_trips(n_rows=5000, n_zones=8, start="2024-01-01", days=14)

    # Write synthetic trips to raw data dir
    raw_trips_path = config.raw_dir / trip_filename(year=2024, month=1)
    raw_trips_path.parent.mkdir(parents=True, exist_ok=True)
    trips_df.to_parquet(raw_trips_path, index=False)
    logger.info("Wrote synthetic trips to %s (%d rows)", raw_trips_path, len(trips_df))

    # Create a minimal taxi_zone_lookup.csv covering the zones used in synthetic data
    # Match the real file's columns: LocationID, Borough, Zone, service_zone
    zones_data = {
        "LocationID": list(range(1, 9)),
        "Borough": ["Manhattan"] * 4 + ["Queens"] * 2 + ["Bronx"] * 2,
        "Zone": [
            "Midtown", "Lower Manhattan", "Upper West Side", "Upper East Side",
            "Astoria", "Long Island City", "Pelham Bay", "Throgs Neck"
        ],
        "service_zone": ["Yellow Zone"] * 8,
    }
    zones_df = pd.DataFrame(zones_data)
    zones_path = config.raw_dir / "taxi_zone_lookup.csv"
    zones_df.to_csv(zones_path, index=False)
    logger.info("Wrote taxi zone lookup to %s (%d zones)", zones_path, len(zones_df))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    main()
