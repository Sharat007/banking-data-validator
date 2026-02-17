# Banking Data Validator

A configurable CSV data validation API for banking data quality checks, built with FastAPI.

## Features

- RESTful API for data validation
- Type-safe Python code with full type annotations
- Comprehensive test coverage (100%)
- Modern Python packaging with `pyproject.toml`
- Code quality tools: Black, Ruff, MyPy

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd banking-data-validator
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# source venv/bin/activate    # On Unix/macOS
```

3. Install dependencies (including dev tools):

```bash
pip install -e ".[dev]"
```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Alternative Documentation: `http://localhost:8000/redoc`

## Development Workflow (TDD)

This project follows Test-Driven Development (TDD) principles:

1. **Write tests first** - Create test cases before implementing features
2. **Run tests** - Ensure they fail initially
3. **Implement feature** - Write minimal code to make tests pass
4. **Refactor** - Clean up code while keeping tests green

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_health_check_returns_200
```

## Code Quality

### Type Checking

```bash
mypy app/
```

### Linting

```bash
# Run Ruff linter
ruff check .

# Auto-fix issues
ruff check --fix .
```

### Code Formatting

```bash
# Format code with Black
black .

# Check formatting without changes
black --check .
```

## Project Structure

```
banking-data-validator/
├── app/                      # Application package
│   ├── __init__.py
│   ├── main.py               # FastAPI application & Pydantic models
│   └── validators.py         # Validation rules engine
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_main.py          # Health endpoint tests
│   └── test_validate.py      # Validation endpoint tests
├── sample_data.csv           # Example CSV with valid & invalid rows
├── pyproject.toml            # Project configuration
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## API Endpoints

### Health Check

- **GET** `/health`
  - Returns service status
  - Response: `{"status": "healthy", "service": "banking-data-validator", "timestamp": "..."}`

### Validate CSV

- **POST** `/validate`
  - Upload a CSV file for validation
  - Validates: required fields, account number format, date format, numeric amounts, currency codes

```bash
curl -X POST http://localhost:8000/validate -F "file=@sample_data.csv"
```

Response:

```json
{
  "file": "sample_data.csv",
  "total_rows": 7,
  "errors_found": 5,
  "valid": false,
  "errors": [
    {
      "row": 3,
      "column": "account_number",
      "message": "Invalid format: 'INVALID' (expected 8-12 digits)",
      "severity": "error"
    },
    {
      "row": 4,
      "column": "transaction_date",
      "message": "Invalid date format: '15-01-2024' (expected YYYY-MM-DD)",
      "severity": "error"
    },
    {
      "row": 5,
      "column": "amount",
      "message": "Required field 'amount' is empty",
      "severity": "error"
    },
    {
      "row": 6,
      "column": "amount",
      "message": "Not a valid number: 'not_a_number'",
      "severity": "error"
    },
    {
      "row": 7,
      "column": "currency",
      "message": "Invalid currency code: 'us' (expected 3-letter ISO like USD, EUR)",
      "severity": "warning"
    }
  ]
}
```

## Contributing

1. Write tests first (TDD)
2. Ensure all tests pass: `pytest`
3. Check type annotations: `mypy app/`
4. Format code: `black .`
5. Lint code: `ruff check .`
6. Commit changes

## License

MIT
