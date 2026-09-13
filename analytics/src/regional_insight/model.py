"""Baseline apartment-price model for an honest, reproducible ML benchmark."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


def train_baseline(apartment_path: Path, artifact_dir: Path) -> dict[str, float | int | str]:
    data = pd.read_csv(apartment_path, encoding="cp949")
    data["trade_price_krw"] = pd.to_numeric(
        data["거래금액"].astype(str).str.replace(",", "", regex=False), errors="coerce"
    ) * 10_000
    features = data[["시군구", "법정동", "전용면적", "층", "건축년도"]].copy()
    target = data["trade_price_krw"]
    valid = target.notna()
    features, target = features[valid], target[valid]

    categorical = ["시군구", "법정동"]
    numeric = ["전용면적", "층", "건축년도"]
    preprocessor = ColumnTransformer(
        [
            (
                "category",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                        ),
                    ]
                ),
                categorical,
            ),
            ("number", SimpleImputer(strategy="median"), numeric),
        ]
    )
    model = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "regressor",
                HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, random_state=42),
            ),
        ]
    )
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )
    model.fit(x_train, y_train)
    prediction = model.predict(x_test)
    metrics: dict[str, float | int | str] = {
        "model": "HistGradientBoostingRegressor",
        "train_rows": len(x_train),
        "test_rows": len(x_test),
        "mae_krw": round(float(mean_absolute_error(y_test, prediction))),
        "r2": round(float(r2_score(y_test, prediction)), 4),
        "split": "random holdout (80/20, random_state=42)",
        "warning": "Learning benchmark only; not an appraisal or investment recommendation.",
    }
    artifact_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact_dir / "housing_price_baseline.joblib")
    (artifact_dir / "model_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metrics

