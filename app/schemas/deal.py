from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PlainSerializer,
    model_validator,
)

class DealStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


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

    @model_validator(mode="after")
    def _validate_currencies_differ(self) -> Self:
        if self.source_currency == self.target_currency:
            raise ValueError(
                "Исходная и целевая валюты не могут совпадать."
            )
        return self


class DealQuoteResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    deal_id: UUID = Field(
        ...,
        description="Уникальный идентификатор возможной сделки",
        examples=["a3b1c2d4-1234-5678-90ab-cdef12345678"],
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
    expires_at: datetime = Field(
        ...,
        description="Время истечения срока действия предложения",
        examples=["2026-10-26T10:30:00Z"],
    )