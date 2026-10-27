from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Query

router = APIRouter(prefix="/deals/reports", tags=["Reports"])


@router.get(
    "/summary",
    summary="Получение агрегированного отчёта по сделкам за интервал времени",
)
def get_deals_summary_report(
    date_from: Annotated[
        datetime,
        Query(description="Начало временного интервала (ISO 8601)"),
    ],
    date_to: Annotated[
        datetime,
        Query(description="Конец временного интервала (ISO 8601)"),
    ],
    currency: Annotated[
        str | None,
        Query(
            pattern=r"^[A-Z]{3}$",
            description="Необязательный фильтр по конкретной валюте (ISO 4217)",
        ),
    ] = None,
) -> dict[str, Any]:
    _ = currency

    return {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "items": [],
    }
