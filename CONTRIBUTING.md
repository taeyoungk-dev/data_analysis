# Contributing

## Local checks

Run the Python lint/tests and the Java tests before committing. Rebuild the analytics marts whenever
raw data or scoring logic changes; CI rejects generated CSV/SQL drift.

## Commit messages

Use a short, descriptive imperative sentence without a Conventional Commits prefix.

Examples:

- `Add district-level housing trend endpoint`
- `의료 접근성 점수 산식 문서화`

Do not use prefixes such as `feat:`, `fix:` or `chore:` in this repository.

