"""Tests for the common UUID parsing helper."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.exceptions import InvalidUUIDError
from app.main import app
from app.services.common_validator import parse_uuid_or_raise

pytestmark = pytest.mark.unit


def test_parse_uuid_or_raise_returns_uuid() -> None:
    value = "a3b1c2d4-1234-5678-90ab-cdef12345678"

    assert str(parse_uuid_or_raise(value)) == value


def test_parse_uuid_or_raise_raises_for_invalid_uuid() -> None:
    with pytest.raises(InvalidUUIDError) as exc_info:
        parse_uuid_or_raise("not-a-uuid", field="deal_id")

    assert exc_info.value.code == "INVALID_UUID"
    assert exc_info.value.field == "deal_id"


async def test_invalid_uuid_is_mapped_to_422() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.patch(
            "/api/v1/deals/not-a-uuid",
            json={"action": "CONFIRM"},
        )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["path", "deal_id"]
