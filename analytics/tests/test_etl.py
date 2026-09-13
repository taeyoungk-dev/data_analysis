from pathlib import Path

import pandas as pd

from regional_insight.etl import build_health_access, build_housing_market


def test_health_etl_joins_population_and_active_clinics(tmp_path: Path) -> None:
    population = tmp_path / "population.csv"
    clinics = tmp_path / "clinics.csv"
    pd.DataFrame(
        [
            {"행정기관": "경기도 A시", "전체": "100,000", "65세이상 전체": "20,000"},
            {"행정기관": "경기도 B시", "전체": "50,000", "65세이상 전체": "15,000"},
        ]
    ).to_csv(population, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {"시군명": "A시", "영업상태명": "영업/정상"},
            {"시군명": "A시", "영업상태명": "폐업"},
            {"시군명": "B시", "영업상태명": "영업중"},
        ]
    ).to_csv(clinics, index=False, encoding="cp949")

    result = build_health_access(population, clinics).set_index("region")

    assert result.loc["A시", "active_clinics"] == 1
    assert result.loc["B시", "elderly_share_pct"] == 30.0


def test_housing_etl_computes_five_year_cagr(tmp_path: Path) -> None:
    paths = []
    for year, price in [(2020, "10,000"), (2024, "20,000")]:
        path = tmp_path / f"apt_{year}.csv"
        pd.DataFrame(
            [
                {
                    "거래금액": price,
                    "년": year,
                    "시군구": "A구",
                    "아파트": "테스트",
                    "전용면적": 100,
                }
            ]
        ).to_csv(path, index=False, encoding="cp949")
        paths.append(path)

    result = build_housing_market(paths)

    assert len(result) == 1
    assert result.loc[0, "transaction_count"] == 1
    assert result.loc[0, "price_cagr_pct"] == 18.92

