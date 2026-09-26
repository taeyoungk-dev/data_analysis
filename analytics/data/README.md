# Data provenance

This repository keeps only the CSV inputs required to reproduce the analytics marts.
They were curated from repositories owned by the project author:

- `gyeonggi_population_2025_04.csv`, `gyeonggi_clinics.csv` —
  [`taeyoungk-dev/android`](https://github.com/taeyoungk-dev/android), source commit `fc6c6d5`
- `senior_disease_specialties.csv` — curated from the `다빈도질병통계.xlsx` reference workbook
  in the same Android project materials. The workbook does not state a base year or geographic
  scope, so these values are exposed as contextual specialty-demand data and never enter the
  regional priority score.
- `seoul_apartments_2020.csv` … `seoul_apartments_2024.csv` —
  [`taeyoungk-dev/python-data-analysis-practice`](https://github.com/taeyoungk-dev/python-data-analysis-practice), source commit `8af74df`

The original notebooks are intentionally not copied because they contain machine-specific paths,
generated outputs and embedded API credentials. The new pipeline replaces those notebooks with
parameterized, tested modules. Public-data ownership and reuse terms remain with each originating
government provider; see the root README for source links and limitations.

The clinic source contains a material number of rows where `시군명` disagrees with the Gyeonggi
road/lot address. The ETL extracts a valid city/county from the address first and uses `시군명` only
as a fallback. This rule is covered by a regression test and prevents shifted regional counts.
