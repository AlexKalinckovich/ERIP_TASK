from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query

from app.api.dependencies import get_report_service, XRequestIdDep
from app.schemas.errors import ErrorResponse, ValidationErrorResponse
from app.schemas.report import SummaryReportResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/deals/reports")

ReportServiceDep = Annotated[ReportService, Depends(get_report_service)]

@router.get(
    "/summary",
    responses={
        200: {
            "model": SummaryReportResponse,
            "description": "Агрегированный отчёт успешно сформирован",
        },
        400: {
            "model": ErrorResponse,
            "description": "Некорректный интервал дат (date_from > date_to)",
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Ошибка валидации формата дат или валюты",
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
        },
    },
    tags=["Reports"],
    summary="Получение агрегированного отчёта по сделкам за интервал времени",
    response_model=SummaryReportResponse,
    response_model_by_alias=True,
)
async def get_deals_summary_report(
    service: ReportServiceDep,
    x_request_id : XRequestIdDep,
    date_from: Annotated[
        datetime,
        Query(
            alias="date_from",
            description="Начало временного интервала (ISO 8601)",
        ),
    ],
    date_to: Annotated[
        datetime,
        Query(
            alias="date_to",
            description="Конец временного интервала (ISO 8601)",
        ),
    ],
    currency: Annotated[
        str | None,
        Query(
            alias="currency",
            pattern=r"^[A-Z]{3}$",
            description="Необязательный фильтр по конкретной валюте (ISO 4217)",
        ),
    ] = None,
) -> SummaryReportResponse:

    return await service.get_deals_summary_report(
        date_from=date_from,
        date_to=date_to,
        currency=currency,
    )
