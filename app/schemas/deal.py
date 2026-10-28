from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
)


class DealStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class DealAction(StrEnum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"


class DealFinalStatus(StrEnum):
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


CurrencyCode = Annotated[
    str,
    Field(pattern=r"^[A-Z]{3}$"),
]

MoneyAmount = Annotated[
    Decimal,
    Field(gt=0, max_digits=15, decimal_places=2),
    PlainSerializer(lambda v: float(v), return_type=float),
]

ExchangeRate = Annotated[
    Decimal,
    Field(gt=0, max_digits=12, decimal_places=4),
    PlainSerializer(lambda v: float(v), return_type=float),
]


class CreateDealRequest(BaseModel):

    model_config = ConfigDict(
        extra="forbid",  
        str_strip_whitespace=True,  
    )

    source_currency: CurrencyCode = Field(
        ...,
        description="Исходная валюта (ISO 4217)",
        examples=["USD"],
    )
    target_currency: CurrencyCode = Field(
        ...,
        description="Целевая валюта (ISO 4217)",
        examples=["BYN"],
    )
    amount: MoneyAmount = Field(
        ...,
        description="Сумма в исходной валюте для обмена",
        examples=[100.00],
    )


class UpdateDealRequest(BaseModel):
    action: DealAction = Field(
        ...,
        description="Решение по сделке (подтвердить или отклонить)",
        examples=["CONFIRM"],
    )


class DealQuoteResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    deal_id: UUID = Field(
        ...,
        description="Уникальный идентификатор возможной сделки",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )
    source_currency: str = Field(..., examples=["USD"])
    target_currency: str = Field(..., examples=["BYN"])
    source_amount: MoneyAmount
    target_amount: MoneyAmount = Field(
        ...,
        description="Рассчитанная сумма в целевой валюте",
        examples=[328.50],
    )
    exchange_rate: ExchangeRate = Field(
        ...,
        description="Курс обмена, применённый к сделке",
        examples=[3.2850],
    )
    status: DealStatus = Field(
        ...,
        description="Текущий статус возможной сделки",
        examples=[DealStatus.PENDING],
    )


class DealStatusResponse(BaseModel):
    deal_id: UUID = Field(
        ...,
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )
    status: DealFinalStatus = Field(
        ...,
        description="Финальный зафиксированный статус сделки",
        examples=["CONFIRMED"],
    )
    updated_at: datetime = Field(
        ...,
        examples=["2026-10-26T10:16:30Z"],
    )


class PendingDealItem(BaseModel):
    deal_id: UUID = Field(
        ...,
        description="Идентификатор сделки",
        examples=["f47ac10b-58cc-4372-a567-0e02b2c3d479"],
    )
    source_currency: str = Field(
        ...,
        description="Исходная валюта",
        examples=["USD"],
    )
    target_currency: str = Field(
        ...,
        description="Целевая валюта",
        examples=["BYN"],
    )
    source_amount: MoneyAmount = Field(
        ...,
        description="Исходная сумма",
        examples=[100.00],
    )
    target_amount: MoneyAmount = Field(
        ...,
        description="Рассчитанная сумма в целевой валюте",
        examples=[328.50],
    )
    exchange_rate: ExchangeRate = Field(
        ...,
        description="Курс обмена",
        examples=[3.2850],
    )
    created_at: datetime | None = Field(
        default=None,
        examples=["2026-10-26T10:15:00Z"],
    )


class PendingDealsResponse(BaseModel):
    total: int = Field(
        ...,
        description="Общее количество активных незавершённых сделок",
        examples=[2],
    )
    limit: int | None = Field(default=None, examples=[20])
    offset: int | None = Field(default=None, examples=[0])
    items: list[PendingDealItem]
