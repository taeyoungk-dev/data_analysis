import pandas as pd

from regional_insight.scoring import health_priority_score, priority_band


def test_health_priority_increases_with_need_and_scarcity() -> None:
    elderly_share = pd.Series([10.0, 20.0, 30.0])
    clinic_supply = pd.Series([20.0, 10.0, 5.0])

    result = health_priority_score(elderly_share, clinic_supply)

    assert result.is_monotonic_increasing
    assert result.iloc[0] == 0.0
    assert result.iloc[-1] == 100.0


def test_priority_band_boundaries() -> None:
    assert priority_band(70) == "HIGH"
    assert priority_band(40) == "WATCH"
    assert priority_band(39.99) == "BALANCED"

