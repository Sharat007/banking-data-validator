"""Banking Data Validator API.

A configurable CSV data validation API for banking data quality checks.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Banking Data Validator",
    description=(
        "A configurable CSV data validation API for banking data quality checks"
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict containing service status and name.
    """
    return {"status": "healthy", "service": "banking-data-validator"}
