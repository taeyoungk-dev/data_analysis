"""Transparent, testable scoring functions used by the ETL pipeline."""

from __future__ import annotations

import pandas as pd


def percentile_score(series: pd.Series, *, ascending: bool = True) -> pd.Series:
    """Return a stable 0-100 percentile score, where a larger result means more priority."""
    if series.empty:
        return series.astype(float)
    rank = series.rank(method="average", pct=True, ascending=ascending)
    return ((rank - rank.min()) / max(rank.max() - rank.min(), 1e-12) * 100).round(2)


def health_priority_score(
    elderly_share_pct: pd.Series, clinics_per_10k_elderly: pd.Series
) -> pd.Series:
    """Weight higher elderly need (55%) and lower clinic supply (45%)."""
    need = percentile_score(elderly_share_pct)
    scarcity = percentile_score(clinics_per_10k_elderly, ascending=False)
    return (need * 0.55 + scarcity * 0.45).round(2)


def market_heat_score(
    median_price_per_sqm: pd.Series, cagr_pct: pd.Series, transaction_count: pd.Series
) -> pd.Series:
    """Summarize current price, five-year movement and liquidity without predicting returns."""
    return (
        percentile_score(median_price_per_sqm) * 0.50
        + percentile_score(cagr_pct) * 0.30
        + percentile_score(transaction_count) * 0.20
    ).round(2)


def priority_band(score: float) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "WATCH"
    return "BALANCED"

