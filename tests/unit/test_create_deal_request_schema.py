from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from openapi_server.models.create_deal_request import CreateDealRequest

pytestmark = pytest.mark.unit
def _payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source_currency": "USD",
        "target_currency": "BYN",
        "amount": 100.00,
    }
    payload.update(overrides)
    return payload


def test_valid_payload_is_parsed() -> None:
    request = CreateDealRequest(**_payload())

    assert request.source_currency == "USD"
    assert request.target_currency == "BYN"
    assert request.amount == pytest.approx(100.00)


def test_integer_amount_is_accepted_as_json_number() -> None:
    request = CreateDealRequest(**_payload(amount=100))

    assert request.amount == 100


def test_amount_lower_boundary_is_inclusive() -> None:
    request = CreateDealRequest(**_payload(amount=0.01))

    assert request.amount == pytest.approx(0.01)


@pytest.mark.parametrize("amount", [0, 0.00, -0.01, -100.00])
def test_amount_must_be_positive(amount: float) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateDealRequest(**_payload(amount=amount))

    errors = exc_info.value.errors()
    assert any(error["loc"][0] == "amount" for error in errors)


@pytest.mark.parametrize("amount", [0.011, 1.999, 100.005])
def test_amount_rejects_more_than_two_decimal_places(amount: float) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateDealRequest(**_payload(amount=amount))

    errors = exc_info.value.errors()
    assert any(error["loc"][0] == "amount" for error in errors)


@pytest.mark.parametrize(
    "field",
    ["source_currency", "target_currency"],
)
@pytest.mark.parametrize(
    "currency_code",
    ["", "US", "USDD", "usd", "U5D", "U S"],
)
def test_currency_code_must_be_three_upper_case_letters(
    field: str,
    currency_code: str,
) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateDealRequest(**_payload(**{field: currency_code}))

    errors = exc_info.value.errors()
    assert any(error["loc"][0] == field for error in errors)


@pytest.mark.parametrize("amount", ["invalid_amount", None, [], {}])
def test_amount_must_be_numeric(amount: Any) -> None:
    with pytest.raises(ValidationError) as exc_info:
        CreateDealRequest(**_payload(amount=amount))

    errors = exc_info.value.errors()
    assert any(error["loc"][0] == "amount" for error in errors)


@pytest.mark.parametrize(
    "missing_field",
    ["source_currency", "target_currency", "amount"],
)
def test_required_fields_are_enforced(missing_field: str) -> None:
    payload = _payload()
    payload.pop(missing_field)

    with pytest.raises(ValidationError) as exc_info:
        CreateDealRequest(**payload)

    errors = exc_info.value.errors()
    assert any(
        error["loc"][0] == missing_field and error["type"] == "missing"
        for error in errors
    )


def test_same_currency_is_not_a_schema_validation_error() -> None:
    request = CreateDealRequest(
        **_payload(source_currency="USD", target_currency="USD")
    )

    assert request.source_currency == request.target_currency == "USD"
