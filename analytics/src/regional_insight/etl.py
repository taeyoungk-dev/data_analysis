"""Build analytics marts from the two source portfolio projects."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .scoring import health_priority_score, market_heat_score, priority_band

ACTIVE_CLINIC_STATUSES = {"영업/정상", "영업중"}
ADDRESS_REGION_PATTERN = r"^경기도\s+([^\s]+(?:시|군))"


def _number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def _load_population(path: Path) -> pd.DataFrame:
    population = pd.read_csv(path, encoding="utf-8-sig")
    population["region"] = population["행정기관"].str.replace("경기도", "", regex=False).str.strip()
    population = population[population["region"].ne("")].copy()
    population["population"] = _number(population["전체"]).astype("int64")
    population["elderly_population"] = _number(population["65세이상 전체"]).astype("int64")
    return population[["region", "population", "elderly_population"]]


def _address_series(clinics: pd.DataFrame) -> pd.Series:
    address = pd.Series(pd.NA, index=clinics.index, dtype="string")
    for column in ("소재지도로명주소", "소재지지번주소"):
        if column in clinics:
            address = address.fillna(clinics[column].astype("string"))
    return address


def _load_active_clinics(path: Path) -> pd.DataFrame:
    clinics = pd.read_csv(path, encoding="cp949")
    active = clinics[clinics["영업상태명"].isin(ACTIVE_CLINIC_STATUSES)].copy()

    declared_region = active["시군명"].astype("string").str.strip()
    address_region = _address_series(active).str.extract(ADDRESS_REGION_PATTERN, expand=False)
    # The source's 시군명 column is shifted for a material number of rows. A valid Gyeonggi
    # address is the more reliable geographic key; the declared value remains the fallback.
    active["region"] = address_region.fillna(declared_region)
    active["latitude"] = (
        _number(active["WGS84위도"])
        if "WGS84위도" in active
        else pd.Series(float("nan"), index=active.index)
    )
    active["longitude"] = (
        _number(active["WGS84경도"])
        if "WGS84경도" in active
        else pd.Series(float("nan"), index=active.index)
    )
    return active


def build_health_access(population_path: Path, clinics_path: Path) -> pd.DataFrame:
    population = _load_population(population_path)
    active = _load_active_clinics(clinics_path)
    clinic_counts = active.groupby("region", as_index=False).size()
    clinic_counts.columns = ["region", "active_clinics"]
    coordinates = (
        active.groupby("region", as_index=False)
        .agg(latitude=("latitude", "median"), longitude=("longitude", "median"))
        .round({"latitude": 6, "longitude": 6})
    )

    result = population.merge(
        clinic_counts, how="left", on="region", validate="one_to_one"
    )
    result = result.merge(coordinates, how="left", on="region", validate="one_to_one")
    result["active_clinics"] = result["active_clinics"].fillna(0).astype("int64")
    result["elderly_share_pct"] = (
        result["elderly_population"] / result["population"] * 100
    ).round(2)
    result["clinics_per_10k_elderly"] = (
        result["active_clinics"] / result["elderly_population"] * 10_000
    ).round(2)
    result["priority_score"] = health_priority_score(
        result["elderly_share_pct"], result["clinics_per_10k_elderly"]
    )
    result["priority_band"] = result["priority_score"].map(priority_band)
    result["period"] = "2025-04"
    return result.sort_values(["priority_score", "region"], ascending=[False, True]).reset_index(
        drop=True
    )


def build_health_specialties(
    population_path: Path, clinics_path: Path, disease_specialties_path: Path
) -> pd.DataFrame:
    population = _load_population(population_path)
    active = _load_active_clinics(clinics_path).reset_index(names="clinic_id")
    disease = pd.read_csv(disease_specialties_path, encoding="utf-8-sig")

    specialty_rows = active[["clinic_id", "region", "진료과목내용"]].copy()
    specialty_rows["specialty"] = specialty_rows["진료과목내용"].fillna("").str.split(",")
    specialty_rows = specialty_rows.explode("specialty")
    specialty_rows["specialty"] = specialty_rows["specialty"].str.strip()
    specialty_rows = specialty_rows.drop_duplicates(["clinic_id", "specialty"])

    regions = population[["region", "elderly_population"]].assign(join_key=1)
    priorities = disease.assign(join_key=1)
    result = regions.merge(priorities, on="join_key", validate="many_to_many").drop(
        columns="join_key"
    )
    counts = (
        specialty_rows[specialty_rows["specialty"].isin(disease["specialty"])]
        .groupby(["region", "specialty"], as_index=False)
        .size()
        .rename(columns={"size": "active_clinics"})
    )
    result = result.merge(counts, how="left", on=["region", "specialty"], validate="one_to_one")
    result["active_clinics"] = result["active_clinics"].fillna(0).astype("int64")
    result["clinics_per_10k_elderly"] = (
        result["active_clinics"] / result["elderly_population"] * 10_000
    ).round(2)
    result = result.rename(columns={"rank": "disease_rank"})
    return result[
        [
            "region",
            "specialty",
            "disease_rank",
            "patient_count",
            "share_pct",
            "active_clinics",
            "clinics_per_10k_elderly",
            "source_scope",
            "source_period",
        ]
    ].sort_values(["region", "disease_rank"])


def build_housing_market(apartment_paths: list[Path]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for path in apartment_paths:
        frame = pd.read_csv(path, encoding="cp949")
        frames.append(frame)
    apartments = pd.concat(frames, ignore_index=True)
    apartments["year"] = _number(apartments["년"])
    apartments["trade_price_krw"] = _number(apartments["거래금액"]) * 10_000
    apartments["area_sqm"] = _number(apartments["전용면적"])
    apartments["price_per_sqm_krw"] = apartments["trade_price_krw"] / apartments["area_sqm"]
    apartments = apartments.dropna(
        subset=["시군구", "year", "trade_price_krw", "area_sqm", "price_per_sqm_krw"]
    )

    annual = (
        apartments.groupby(["시군구", "year"])
        .agg(annual_median_price_per_sqm=("price_per_sqm_krw", "median"))
        .reset_index()
    )
    start = annual[annual["year"].eq(2020)].set_index("시군구")["annual_median_price_per_sqm"]
    end = annual[annual["year"].eq(2024)].set_index("시군구")["annual_median_price_per_sqm"]
    cagr = (((end / start) ** (1 / 4) - 1) * 100).rename("price_cagr_pct")

    latest = apartments[apartments["year"].eq(2024)]
    result = (
        latest.groupby("시군구")
        .agg(
            transaction_count=("아파트", "size"),
            median_trade_price_krw=("trade_price_krw", "median"),
            median_price_per_sqm_krw=("price_per_sqm_krw", "median"),
            median_area_sqm=("area_sqm", "median"),
        )
        .join(cagr, how="left")
        .reset_index(names="region")
    )
    result["price_cagr_pct"] = result["price_cagr_pct"].round(2)
    result["median_trade_price_krw"] = result["median_trade_price_krw"].round().astype("int64")
    result["median_price_per_sqm_krw"] = (
        result["median_price_per_sqm_krw"].round().astype("int64")
    )
    result["median_area_sqm"] = result["median_area_sqm"].round(2)
    result["market_heat_score"] = market_heat_score(
        result["median_price_per_sqm_krw"],
        result["price_cagr_pct"],
        result["transaction_count"],
    )
    result["market_band"] = result["market_heat_score"].map(priority_band)
    result["period"] = "2024"
    return result.sort_values(
        ["market_heat_score", "region"], ascending=[False, True]
    ).reset_index(drop=True)
