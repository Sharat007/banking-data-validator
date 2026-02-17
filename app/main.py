"""Banking Data Validator API.

A configurable CSV data validation API for banking data quality checks.
"""

import csv
import io
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.validators import validate_rows

app = FastAPI(
    title="Banking Data Validator",
    description="Validate banking CSV data against configurable rules",
    version="0.2.0",
)

_file_upload = File(...)


class ValidationError(BaseModel):
    row: int
    column: str
    message: str
    severity: str = "error"


class ValidationReport(BaseModel):
    file: str
    total_rows: int
    errors_found: int
    valid: bool
    errors: list[ValidationError]


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(
        status="healthy",
        service="banking-data-validator",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/validate", response_model=ValidationReport)
async def validate_csv(file: UploadFile = _file_upload) -> Any:
    """Upload a CSV file and validate it against banking data rules.

    Accepts a CSV file with columns like account_number, transaction_date,
    amount, and currency. Returns a structured validation report.
    """
    if not file.filename or not file.filename.endswith(".csv"):
        return JSONResponse(
            status_code=400,
            content={"error": "Only CSV files are accepted"},
        )

    contents = await file.read()
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        return JSONResponse(
            status_code=400,
            content={"error": "File must be UTF-8 encoded"},
        )

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)

    if not rows:
        return JSONResponse(
            status_code=400,
            content={"error": "CSV file is empty or has no data rows"},
        )

    errors = validate_rows(rows)

    return ValidationReport(
        file=file.filename,
        total_rows=len(rows),
        errors_found=len(errors),
        valid=len(errors) == 0,
        errors=[ValidationError(**e) for e in errors],
    )
