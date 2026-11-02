# Contributing

## Local checks

Run `make check` (Ruff, pytest, Gradle tests and the Playwright dashboard E2E) before committing.
Install the tools once with `python -m pip install -e './analytics[dev,e2e]'` and
`python -m playwright install chromium`.

Rebuild the analytics marts with `make analytics` whenever raw data or scoring logic changes; CI
rejects generated CSV/SQL drift. V2/V3 are already-applied Flyway migrations: a data refresh for an
existing database must be added as a new versioned migration instead of editing them.

## Commit messages

Use a short, descriptive imperative sentence without a Conventional Commits prefix.

Examples:

- `Add district-level housing trend endpoint`
- `의료 접근성 점수 산식 문서화`

Do not use prefixes such as `feat:`, `fix:` or `chore:` in this repository.

