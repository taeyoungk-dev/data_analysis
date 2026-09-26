# Data dictionary

## `health_access_metric`

| Column | Meaning |
|---|---|
| `region` | Gyeonggi city/county name |
| `population` | Registered population, April 2025 |
| `elderly_population` | Registered residents aged 65+, April 2025 |
| `active_clinics` | Clinic records whose status is `영업/정상` or `영업중` |
| `elderly_share_pct` | `elderly_population / population × 100` |
| `clinics_per_10k_elderly` | Active clinics per 10,000 elderly residents |
| `priority_score` | 55% elderly-share percentile + 45% inverse clinic-supply percentile |
| `priority_band` | `HIGH` ≥ 70, `WATCH` ≥ 40, otherwise `BALANCED` |
| `latitude` | Median latitude of active clinic addresses in the region |
| `longitude` | Median longitude of active clinic addresses in the region |

The score is a screening signal, not a causal measure of healthcare outcomes. It does not account
for hospital capacity, specialties, travel time, quality, cross-border visits or address anomalies.

Clinic rows use the city/county parsed from a valid Gyeonggi road or lot address. The supplied
`시군명` is used only when an address-derived region is unavailable.

## `health_specialty_metric`

| Column | Meaning |
|---|---|
| `region` | Gyeonggi city/county name after address normalization |
| `specialty` | Specialty listed in the senior disease reference profile |
| `disease_rank` | Rank in the supplied frequent-disease specialty table |
| `disease_patient_count` | Patient count in the supplied reference table |
| `disease_share_pct` | Share of patients among the seven supplied specialties |
| `active_clinics` | Active clinics in the region listing the specialty |
| `clinics_per_10k_elderly` | Specialty-listing clinics per 10,000 elderly residents |
| `source_scope` | Human-readable description of the reference profile |
| `source_period` | Source period label; `기준연도 미기재` when the workbook omits it |

The disease profile provides context only. Its missing period and geographic scope make it
unsuitable for the regional priority score or for causal claims about unmet demand.

## `housing_market_metric`

| Column | Meaning |
|---|---|
| `region` | Seoul autonomous district |
| `transaction_count` | Apartment sale records in 2024 |
| `median_trade_price_krw` | Median registered transaction price in KRW |
| `median_price_per_sqm_krw` | Median price per exclusive-area square metre |
| `median_area_sqm` | Median exclusive area |
| `price_cagr_pct` | CAGR of district median price/㎡ from 2020 to 2024 |
| `market_heat_score` | 50% price percentile + 30% CAGR percentile + 20% volume percentile |
| `market_band` | `HIGH` ≥ 70, `WATCH` ≥ 40, otherwise `BALANCED` |

The score describes observed market intensity. It is not a forecast, valuation, affordability
measure or investment recommendation. Registered trades may be revised or cancelled after capture.
