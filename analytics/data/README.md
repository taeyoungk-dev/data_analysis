# Data provenance

This repository keeps only the CSV inputs required to reproduce the two analytics marts.
They were curated from repositories owned by the project author:

- `gyeonggi_population_2025_04.csv`, `gyeonggi_clinics.csv` —
  [`taeyoungk-dev/android`](https://github.com/taeyoungk-dev/android), source commit `fc6c6d5`
- `seoul_apartments_2020.csv` … `seoul_apartments_2024.csv` —
  [`taeyoungk-dev/python-data-analysis-practice`](https://github.com/taeyoungk-dev/python-data-analysis-practice), source commit `8af74df`

The original notebooks are intentionally not copied because they contain machine-specific paths,
generated outputs and embedded API credentials. The new pipeline replaces those notebooks with
parameterized, tested modules. Public-data ownership and reuse terms remain with each originating
government provider; see the root README for source links and limitations.

