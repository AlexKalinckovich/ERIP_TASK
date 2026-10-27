from app.core.exceptions import DealValidationError
from app.schemas.deal import CreateDealRequest


class DealValidator:
    def validate_create_request(self, request: CreateDealRequest) -> None:
        if request.source_currency == request.target_currency:
            raise DealValidationError(
                code="SAME_CURRENCY_NOT_ALLOWED",
                message="Исходная и целевая валюты не могут совпадать.",
            )
