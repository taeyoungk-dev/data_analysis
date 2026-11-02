import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from regional_insight.etl import build_health_access, build_housing_market
from regional_insight.export import export_outputs, validate_marts


def _health() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "region": "A시",
                "population": 100,
                "elderly_population": 20,
                "active_clinics": 1,
                "elderly_share_pct": 20.0,
                "clinics_per_10k_elderly": 500.0,
                "priority_score": 50.0,
                "priority_band": "WATCH",
                "period": "2025-04",
                "latitude": float("nan"),
                "longitude": 127.0,
            }
        ]
    )


def _housing(cagr: float = 3.5) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "region": "O'Brien구",
                "transaction_count": 3,
                "median_trade_price_krw": 1_000_000_000,
                "median_price_per_sqm_krw": 12_000_000,
                "median_area_sqm": 84.0,
                "price_cagr_pct": cagr,
                "market_heat_score": 60.0,
                "market_band": "WATCH",
                "period": "2024",
            }
        ]
    )


def _specialties() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "region": "A시",
                "specialty": "내과",
                "disease_rank": 1,
                "patient_count": 10,
                "share_pct": 50.0,
                "active_clinics": 1,
                "clinics_per_10k_elderly": 500.0,
                "source_scope": "test",
                "source_period": "test",
            }
        ]
    )


def _export(tmp_path: Path, housing: pd.DataFrame, specialties: pd.DataFrame | None = None):
    export_outputs(
        _health(),
        housing,
        _specialties() if specialties is None else specialties,
        tmp_path / "processed",
        tmp_path / "V2.sql",
        tmp_path / "V3.sql",
    )


def test_export_writes_escaped_sql_and_null_coordinates(tmp_path: Path) -> None:
    _export(tmp_path, _housing())

    seed = (tmp_path / "V2.sql").read_text(encoding="utf-8")
    profile = (tmp_path / "V3.sql").read_text(encoding="utf-8")
    assert "'O''Brien구'" in seed
    assert "latitude = NULL, longitude = 127.0" in profile
    assert "nan" not in seed.lower() and "nan" not in profile.lower()


def test_export_rejects_missing_required_value_instead_of_writing_nan(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="price_cagr_pct"):
        _export(tmp_path, _housing(cagr=float("nan")))
    assert not (tmp_path / "V2.sql").exists()


def test_validate_marts_rejects_duplicate_keys() -> None:
    duplicated = pd.concat([_specialties(), _specialties()], ignore_index=True)
    with pytest.raises(ValueError, match="duplicate"):
        validate_marts(
            {"health_access": _health(), "housing_market": _housing(), "health_specialties": duplicated}
        )


def test_housing_district_without_2020_trades_cannot_reach_the_seed(tmp_path: Path) -> None:
    paths = []
    for year, regions in [(2020, ["A구"]), (2024, ["A구", "B구"])]:
        path = tmp_path / f"apt_{year}.csv"
        pd.DataFrame(
            [
                {"거래금액": "10,000", "년": year, "시군구": region, "아파트": "t", "전용면적": 84}
                for region in regions
            ]
        ).to_csv(path, index=False, encoding="cp949")
        paths.append(path)

    housing = build_housing_market(paths)

    assert pd.isna(housing.set_index("region").loc["B구", "price_cagr_pct"])  # no 2020 baseline
    with pytest.raises(ValueError, match="price_cagr_pct"):
        _export(tmp_path, housing)


def test_health_etl_rejects_clinics_outside_known_population_regions(tmp_path: Path) -> None:
    population = tmp_path / "population.csv"
    clinics = tmp_path / "clinics.csv"
    pd.DataFrame(
        [{"행정기관": "경기도 A시", "전체": "100", "65세이상 전체": "20"}]
    ).to_csv(population, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [{"시군명": "A시", "영업상태명": "영업중", "소재지도로명주소": "경기도 Z시 테스트로 1"}]
    ).to_csv(clinics, index=False, encoding="cp949")

    with pytest.raises(ValueError, match="Z시"):
        build_health_access(population, clinics)


def test_cli_build_does_not_import_scikit_learn() -> None:
    code = "import sys, regional_insight.cli; print('sklearn' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "False"
