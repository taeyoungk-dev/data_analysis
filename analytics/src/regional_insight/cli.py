"""Command-line entry point for analytics build and model training."""

from __future__ import annotations

import argparse
from pathlib import Path

from .etl import build_health_access, build_housing_market
from .export import export_outputs
from .model import train_baseline

ANALYTICS_DIR = Path(__file__).resolve().parents[2]
REPOSITORY_DIR = ANALYTICS_DIR.parent
RAW_DIR = ANALYTICS_DIR / "data" / "raw"
PROCESSED_DIR = ANALYTICS_DIR / "data" / "processed"
ARTIFACT_DIR = ANALYTICS_DIR / "artifacts"
MIGRATION_PATH = (
    REPOSITORY_DIR / "backend" / "src" / "main" / "resources" / "db" / "migration"
    / "V2__seed_analytics.sql"
)


def build() -> None:
    health = build_health_access(
        RAW_DIR / "gyeonggi_population_2025_04.csv", RAW_DIR / "gyeonggi_clinics.csv"
    )
    housing = build_housing_market(sorted(RAW_DIR.glob("seoul_apartments_*.csv")))
    export_outputs(health, housing, PROCESSED_DIR, MIGRATION_PATH)
    print(f"Built {len(health)} health rows and {len(housing)} housing rows.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Regional Insight Korea analytics pipeline")
    parser.add_argument("command", choices=["build", "train", "all"])
    args = parser.parse_args()
    if args.command in {"build", "all"}:
        build()
    if args.command in {"train", "all"}:
        metrics = train_baseline(RAW_DIR / "seoul_apartments_2024.csv", ARTIFACT_DIR)
        print(metrics)


if __name__ == "__main__":
    main()

