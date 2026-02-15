"""Tests for the /validate endpoint."""

import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _upload_csv(content: str, filename: str = "test.csv"):
    """Helper to upload CSV content to the validate endpoint."""
    return client.post(
        "/validate",
        files={"file": (filename, io.BytesIO(content.encode()), "text/csv")},
    )


class TestValidateEndpoint:
    """Tests for POST /validate."""

    def test_valid_csv_returns_no_errors(self):
        csv = "account_number,transaction_date,amount,currency\n12345678,2024-01-15,100.50,USD\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert resp.status_code == 200
        assert data["valid"] is True
        assert data["errors_found"] == 0
        assert data["total_rows"] == 1

    def test_missing_required_field_amount(self):
        csv = "account_number,transaction_date,amount\n12345678,2024-01-15,\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "amount" for e in data["errors"])

    def test_invalid_account_number_format(self):
        csv = "account_number,transaction_date,amount\nABC,2024-01-15,100\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "account_number" for e in data["errors"])

    def test_invalid_date_format(self):
        csv = "account_number,transaction_date,amount\n12345678,01-15-2024,100\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "transaction_date" for e in data["errors"])

    def test_non_numeric_amount(self):
        csv = "account_number,transaction_date,amount\n12345678,2024-01-15,abc\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "amount" for e in data["errors"])

    def test_invalid_currency_code(self):
        csv = "account_number,transaction_date,amount,currency\n12345678,2024-01-15,100,us\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["valid"] is False
        assert any(e["column"] == "currency" for e in data["errors"])

    def test_rejects_non_csv_file(self):
        resp = client.post(
            "/validate",
            files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert resp.status_code == 400

    def test_empty_csv_returns_400(self):
        resp = _upload_csv("account_number,transaction_date,amount\n")
        assert resp.status_code == 400

    def test_multiple_errors_in_one_row(self):
        csv = "account_number,transaction_date,amount\nBAD,not-a-date,xyz\n"
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["errors_found"] >= 3

    def test_multiple_rows_mixed_valid_invalid(self):
        csv = (
            "account_number,transaction_date,amount\n"
            "12345678,2024-01-15,100\n"
            "BAD,2024-01-15,100\n"
            "12345678,2024-01-15,200\n"
        )
        resp = _upload_csv(csv)
        data = resp.json()
        assert data["total_rows"] == 3
        assert data["valid"] is False
        assert all(e["row"] == 2 for e in data["errors"])