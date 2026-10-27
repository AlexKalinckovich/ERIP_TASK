from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Annotated, Any, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Query, Response, status
from pydantic import BaseModel, Field

from app.schemas.deal import CreateDealRequest, DealQuoteResponse, DealStatus

router = APIRouter(prefix="/deals", tags=["Deals"])

_STUB_RATE = Decimal("3.2850")
_STUB_TTL = timedelta(minutes=15)
_MAX_AMOUNT = Decimal("9999999999999.99")


class UpdateDealRequest(BaseModel):
    action: Literal["CONFIRM", "REJECT"] = Field(
        ...,
        description="Решение по сделке (подтвердить или отклонить)",
        examples=["CONFIRM"],
    )


@router.post(
    "",
    response_model=DealQuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание предварительной сделки на обмен валют",
)
def create_deal_quote(
    payload: CreateDealRequest,
    response: Response,
) -> DealQuoteResponse:
    """Return a stub quote and the ``Location`` of the created resource."""

    deal_id = uuid4()
    target_amount = min(
        (payload.amount * _STUB_RATE).quantize(Decimal("0.01")),
        _MAX_AMOUNT,
    )

    response.headers["Location"] = f"/api/v1/deals/{deal_id}"

    return DealQuoteResponse(
        deal_id=deal_id,
        source_currency=payload.source_currency,
        target_currency=payload.target_currency,
        source_amount=payload.amount,
        target_amount=target_amount,
        exchange_rate=_STUB_RATE,
        status=DealStatus.PENDING,
        expires_at=datetime.now(UTC) + _STUB_TTL,
    )


@router.get(
    "/pending",
    summary="Получение списка незавершённых сделок",
)
def get_pending_deals(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict[str, Any]:
    return {"items": [], "total": 0, "limit": limit, "offset": offset}


@router.patch(
    "/{deal_id}",
    summary="Подтверждение или отклонение обмена валют",
)
def update_deal_status(
    deal_id: UUID,
    payload: UpdateDealRequest,
) -> dict[str, Any]:
    return {
        "deal_id": str(deal_id),
        "status": "CONFIRMED" if payload.action == "CONFIRM" else "REJECTED",
        "updated_at": datetime.now(UTC).isoformat(),
    }
