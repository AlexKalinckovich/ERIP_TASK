import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

pytestmark = pytest.mark.unit


async def test_deal_validation_error_returns_400() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/api/v1/deals",
            json={
                "source_currency": "USD",
                "target_currency": "USD",
                "amount": 100.0,
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "code": "SAME_CURRENCY_NOT_ALLOWED",
        "message": "Исходная и целевая валюты не могут совпадать.",
        "details": None,
    }
