from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, PlainSerializer

from app.schemas.deal import CurrencyCode

ReportAmount = Annotated[
    Decimal,
    Field(ge=0, max_digits=15, decimal_places=2),
    PlainSerializer(lambda v: float(v), return_type=float),
]
class SummaryReportItem(BaseModel):
    currency: CurrencyCode = Field(
        ...,
        description="Валюта операции",
        examples=["USD"],
    )
    total_received: ReportAmount = Field(
        ...,
        description="Общая сумма данной валюты, поступившая в кассу",
        examples=[15000.00],
    )
    total_given: ReportAmount = Field(
        ...,
        description="Общая сумма данной валюты, выданная из кассы",
        examples=[49200.00],
    )
    deal_count: int = Field(
        ...,
        ge=0,
        description="Количество успешно зафиксированных сделок с данной валютой",
        examples=[45],
    )
class SummaryReportResponse(BaseModel):
    date_from: datetime = Field(
        ...,
        description="Начало временного интервала",
        examples=["2026-10-01T00:00:00Z"],
    )
    date_to: datetime = Field(
        ...,
        description="Конец временного интервала",
        examples=["2026-10-26T23:59:59Z"],
    )
    items: list[SummaryReportItem] = Field(
        ...,
        description="Агрегированные показатели по валютам",
    )
