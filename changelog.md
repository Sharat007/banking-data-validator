# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2026-02-17

### Added

- GitHub Actions CI pipeline (lint, format, type check, tests on every push)
- Full PEP 8 compliance with strict Ruff, Black, and MyPy checks

## [0.2.0] - 2026-02-17

### Added

- Duplicate transaction detection (warning severity)
- Dockerfile and docker-compose.yml for containerized deployment
- Deployed to Render: https://banking-data-validator.onrender.com
- `.dockerignore` for lean Docker builds

### Fixed

- Proper duplicate detection across multiple duplicate rows
- `sample_data.csv` tracked in git (removed blanket `*.csv` from gitignore)

## [0.1.0] - 2026-02-17

### Added

- `/health` endpoint with service status and timestamp
- `/validate` endpoint — upload CSV, get structured validation report
- 5 banking validation rules: required fields, account number format, date format, numeric amount, currency code
- Pydantic response models for type-safe API responses
- Missing column detection and real calendar date validation
- Comprehensive test suite with 100% coverage
- Modern Python packaging with `pyproject.toml`
- Code quality tooling: Black, Ruff, MyPy
- TDD workflow
- Sample data file for testing
