# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.reports_api_base import BaseReportsApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.summary_report_response import SummaryReportResponse
from openapi_server.models.validation_error_response import ValidationErrorResponse


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/api/v1/deals/reports/summary",
    responses={
        200: {"model": SummaryReportResponse, "description": "Агрегированный отчёт успешно сформирован"},
        400: {"model": ErrorResponse, "description": "Некорректный интервал дат (date_from &gt; date_to)"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации формата дат или валюты"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    tags=["Reports"],
    summary="Получение агрегированного отчёта по сделкам за интервал времени",
    response_model_by_alias=True,
)
async def get_deals_summary_report(
    date_from: str = Query(None, description="Начало временного интервала (ISO 8601)", alias="date_from"),
    date_to: str = Query(None, description="Конец временного интервала (ISO 8601)", alias="date_to"),
    currency: str = Query(None, description="Необязательный фильтр по конкретной валюте (ISO 4217)", alias="currency", regex=r"/^[A-Z]{3}$/"),
    x_request_id: str = Header(None, description="Идентификатор корреляции для сквозного логирования"),
) -> SummaryReportResponse:
    """Возвращает сводную статистику движения денежных средств в кассе (сумма полученного,  сумма ушедшего, количество сделок) по каждой валюте за указанный интервал времени. """
    return BaseReportsApi.subclasses[0]().get_deals_summary_report(date_from, date_to, currency, x_request_id)
