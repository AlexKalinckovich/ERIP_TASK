from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from app.schemas.deal import (
    CreateDealRequest,
    DealAction,
    DealFinalStatus,
    DealQuoteResponse,
    DealStatus,
    DealStatusResponse,
    PendingDealsResponse,
    UpdateDealRequest,
)
from app.services.deal_validator import DealValidator


class DealService:
    _STUB_RATE = Decimal("3.2850")
    _STUB_TTL = timedelta(minutes=15)
    _MAX_AMOUNT = Decimal("9999999999999.99")

    def __init__(self, validator: DealValidator) -> None:
        self._validator = validator

    async def create_deal(
        self,
        request: CreateDealRequest,
    ) -> DealQuoteResponse:
        self._validator.validate_create_request(request)

        deal_id = uuid4()
        target_amount = min(
            (request.amount * self._STUB_RATE).quantize(Decimal("0.01")),
            self._MAX_AMOUNT,
        )

        return DealQuoteResponse(
            deal_id=deal_id,
            source_currency=request.source_currency,
            target_currency=request.target_currency,
            source_amount=request.amount,
            target_amount=target_amount,
            exchange_rate=self._STUB_RATE,
            status=DealStatus.PENDING,
            expires_at=datetime.now(UTC) + self._STUB_TTL,
        )

    async def get_pending_deals(
        self,
        limit: int,
        offset: int,
    ) -> PendingDealsResponse:
        return PendingDealsResponse(
            total=0,
            limit=limit,
            offset=offset,
            items=[],
        )

    async def update_deal_status(
        self,
        deal_id: UUID,
        request: UpdateDealRequest,
    ) -> DealStatusResponse:
        final_status = (
            DealFinalStatus.CONFIRMED
            if request.action == DealAction.CONFIRM
            else DealFinalStatus.REJECTED
        )

        return DealStatusResponse(
            deal_id=deal_id,
            status=final_status,
            updated_at=datetime.now(UTC),
        )
