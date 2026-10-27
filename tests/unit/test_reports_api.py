"""API-level tests for the deals summary report stub."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.unit


async def test_get_deals_summary_report_returns_stub() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/deals/reports/summary",
            params={
                "date_from": "2026-10-01T00:00:00Z",
                "date_to": "2026-10-26T23:59:59Z",
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "date_from": "2026-10-01T00:00:00Z",
        "date_to": "2026-10-26T23:59:59Z",
        "items": [],
    }


async def test_get_deals_summary_report_rejects_invalid_date_range() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/deals/reports/summary",
            params={
                "date_from": "2026-10-27T00:00:00Z",
                "date_to": "2026-10-01T00:00:00Z",
            },
        )

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_DATE_RANGE"


async def test_get_deals_summary_report_rejects_invalid_currency() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/api/v1/deals/reports/summary",
            params={
                "date_from": "2026-10-01T00:00:00Z",
                "date_to": "2026-10-26T23:59:59Z",
                "currency": "usd",
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "currency"]
