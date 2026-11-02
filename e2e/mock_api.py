"""Static dashboard + contract-compatible mock of the Spring REST API for browser tests.

The mock reads the committed analytics marts (``analytics/data/processed``), so the browser sees
the same values the Flyway seed loads into PostgreSQL. It is a test double for the Java API, not
a replacement: API behaviour itself is covered by the JUnit/MockMvc suite.
"""

from __future__ import annotations

import csv
import json
import threading
from functools import partial
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import ClassVar
from urllib.parse import parse_qs, unquote, urlparse

REPOSITORY_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = REPOSITORY_DIR / "backend" / "src" / "main" / "resources" / "static"
PROCESSED_DIR = REPOSITORY_DIR / "analytics" / "data" / "processed"


def _rows(name: str) -> list[dict[str, str]]:
    with (PROCESSED_DIR / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _number(value: str) -> float | int | None:
    if value in ("", "nan", "NaN"):
        return None
    number = float(value)
    return int(number) if number.is_integer() and "." not in value else number


def load_data() -> dict[str, list[dict[str, object]]]:
    health = [
        {
            "region": row["region"],
            "population": _number(row["population"]),
            "elderlyPopulation": _number(row["elderly_population"]),
            "activeClinics": _number(row["active_clinics"]),
            "elderlySharePct": _number(row["elderly_share_pct"]),
            "clinicsPer10kElderly": _number(row["clinics_per_10k_elderly"]),
            "priorityScore": _number(row["priority_score"]),
            "priorityBand": row["priority_band"],
            "period": row["period"],
            "latitude": _number(row["latitude"]),
            "longitude": _number(row["longitude"]),
        }
        for row in _rows("health_access.csv")
    ]
    health.sort(key=lambda item: (-item["priorityScore"], item["region"]))
    housing = [
        {
            "region": row["region"],
            "transactionCount": _number(row["transaction_count"]),
            "medianTradePriceKrw": _number(row["median_trade_price_krw"]),
            "medianPricePerSqmKrw": _number(row["median_price_per_sqm_krw"]),
            "medianAreaSqm": _number(row["median_area_sqm"]),
            "priceCagrPct": _number(row["price_cagr_pct"]),
            "marketHeatScore": _number(row["market_heat_score"]),
            "marketBand": row["market_band"],
            "period": row["period"],
        }
        for row in _rows("housing_market.csv")
    ]
    housing.sort(key=lambda item: (-item["marketHeatScore"], item["region"]))
    specialties = [
        {
            "region": row["region"],
            "specialty": row["specialty"],
            "diseaseRank": _number(row["disease_rank"]),
            "diseasePatientCount": _number(row["patient_count"]),
            "diseaseSharePct": _number(row["share_pct"]),
            "activeClinics": _number(row["active_clinics"]),
            "clinicsPer10kElderly": _number(row["clinics_per_10k_elderly"]),
            "sourceScope": row["source_scope"],
            "sourcePeriod": row["source_period"],
        }
        for row in _rows("health_specialties.csv")
    ]
    specialties.sort(key=lambda item: (item["region"], item["diseaseRank"]))
    return {"health": health, "housing": housing, "specialties": specialties}


class DashboardHandler(SimpleHTTPRequestHandler):
    data: ClassVar[dict[str, list[dict[str, object]]]] = {}

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        content_type = "application/problem+json" if status >= 400 else "application/json"
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _problem(self, status: HTTPStatus, detail: str) -> None:
        self._json({"status": status.value, "title": status.phrase, "detail": detail}, status)

    def _limit(self, query: dict[str, list[str]], maximum: int) -> int | None:
        raw = query.get("limit", ["10"])[0]
        if not raw.isdigit() or not 1 <= int(raw) <= maximum:
            self._problem(HTTPStatus.BAD_REQUEST, "Request parameter validation failed")
            return None
        return int(raw)

    def do_GET(self) -> None:
        url = urlparse(self.path)
        path = unquote(url.path)
        query = parse_qs(url.query)
        health, housing = self.data["health"], self.data["housing"]
        if path == "/actuator/health":
            return self._json({"status": "UP"})
        if path == "/api/v1/overview":
            return self._json(
                {
                    "healthRegions": len(health),
                    "highPriorityRegions": sum(item["priorityBand"] == "HIGH" for item in health),
                    "activeClinics": sum(item["activeClinics"] for item in health),
                    "housingRegions": len(housing),
                    "highestHealthPriority": health[0] if health else None,
                    "hottestHousingMarket": housing[0] if housing else None,
                    "generatedFrom": "Korean public data, 2020-2025",
                }
            )
        if path == "/api/v1/health-access":
            limit = self._limit(query, 31)
            return None if limit is None else self._json(health[:limit])
        if path == "/api/v1/housing":
            limit = self._limit(query, 25)
            return None if limit is None else self._json(housing[:limit])
        if path.startswith("/api/v1/health-access/") and path.endswith("/specialties"):
            region = path.removeprefix("/api/v1/health-access/").removesuffix("/specialties")
            if not any(item["region"] == region for item in health):
                return self._problem(HTTPStatus.NOT_FOUND, f"No health-access metric: {region}")
            return self._json([s for s in self.data["specialties"] if s["region"] == region])
        if path.startswith(("/api/", "/actuator/")):
            return self._problem(HTTPStatus.NOT_FOUND, "No endpoint")
        return super().do_GET()


def start_server(port: int = 0) -> tuple[ThreadingHTTPServer, str]:
    """Start the server on a background thread and return it with its base URL."""
    DashboardHandler.data = load_data()
    handler = partial(DashboardHandler, directory=str(STATIC_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}"


if __name__ == "__main__":
    running, base_url = start_server(8085)
    print(f"Dashboard with mock API: {base_url}  (Ctrl+C to stop)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        running.shutdown()
