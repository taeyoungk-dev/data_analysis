from pathlib import Path

import pandas as pd

from regional_insight.etl import build_health_access, build_health_specialties, build_housing_market


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


def test_health_etl_prefers_address_region_when_declared_region_is_wrong(tmp_path: Path) -> None:
    population = tmp_path / "population.csv"
    clinics = tmp_path / "clinics.csv"
    pd.DataFrame(
        [
            {"행정기관": "경기도 A시", "전체": "100,000", "65세이상 전체": "20,000"},
            {"행정기관": "경기도 B시", "전체": "50,000", "65세이상 전체": "10,000"},
        ]
    ).to_csv(population, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {
                "시군명": "A시",
                "영업상태명": "영업/정상",
                "소재지도로명주소": "경기도 B시 테스트로 1",
            }
        ]
    ).to_csv(clinics, index=False, encoding="cp949")

    result = build_health_access(population, clinics).set_index("region")

    assert result.loc["A시", "active_clinics"] == 0
    assert result.loc["B시", "active_clinics"] == 1


def test_health_specialties_crosses_demand_profile_with_local_supply(tmp_path: Path) -> None:
    population = tmp_path / "population.csv"
    clinics = tmp_path / "clinics.csv"
    disease = tmp_path / "disease.csv"
    pd.DataFrame(
        [{"행정기관": "경기도 A시", "전체": "100,000", "65세이상 전체": "20,000"}]
    ).to_csv(population, index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {
                "시군명": "A시",
                "영업상태명": "영업/정상",
                "진료과목내용": "내과, 안과",
                "소재지도로명주소": "경기도 A시 테스트로 1",
            },
            {
                "시군명": "A시",
                "영업상태명": "영업/정상",
                "진료과목내용": "내과",
                "소재지도로명주소": "경기도 A시 테스트로 2",
            },
        ]
    ).to_csv(clinics, index=False, encoding="cp949")
    pd.DataFrame(
        [
            {
                "admission_type": "입원",
                "rank": 1,
                "specialty": "내과",
                "patient_count": 80,
                "share_pct": 80,
                "source_scope": "test",
                "source_period": "test",
            },
            {
                "admission_type": "입원",
                "rank": 2,
                "specialty": "신경과",
                "patient_count": 20,
                "share_pct": 20,
                "source_scope": "test",
                "source_period": "test",
            },
        ]
    ).to_csv(disease, index=False, encoding="utf-8-sig")

    result = build_health_specialties(population, clinics, disease).set_index("specialty")

    assert result.loc["내과", "active_clinics"] == 2
    assert result.loc["내과", "clinics_per_10k_elderly"] == 1.0
    assert result.loc["신경과", "active_clinics"] == 0


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
