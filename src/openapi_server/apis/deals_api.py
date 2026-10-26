# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.deals_api_base import BaseDealsApi
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
from openapi_server.models.create_deal_request import CreateDealRequest
from openapi_server.models.deal_quote_response import DealQuoteResponse
from openapi_server.models.deal_status_response import DealStatusResponse
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.pending_deals_response import PendingDealsResponse
from openapi_server.models.update_deal_request import UpdateDealRequest
from openapi_server.models.validation_error_response import ValidationErrorResponse


router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/api/v1/deals",
    responses={
        201: {"model": DealQuoteResponse, "description": "Предварительная сделка успешно создана"},
        400: {"model": ErrorResponse, "description": "Ошибка бизнес-логики (одинаковые валюты, отсутствие курса)"},
        409: {"model": ErrorResponse, "description": "Конфликт ключа идемпотентности"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации входных данных (Pydantic Validation Error)"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
        503: {"model": ErrorResponse, "description": "Сервис или База Данных временно недоступны"},
    },
    tags=["Deals"],
    summary="Создание предварительной сделки на обмен валют",
    response_model_by_alias=True,
)
async def create_deal_quote(
    create_deal_request: CreateDealRequest = Body(None, description=""),
    idempotency_key: str = Header(None, description="Уникальный ключ идемпотентности запроса (UUID v4)"),
    x_request_id: str = Header(None, description="Идентификатор корреляции для сквозного логирования"),
) -> DealQuoteResponse:
    """Рассчитывает параметры обмена на основе текущих курсов НБ РБ. """
    return BaseDealsApi.subclasses[0]().create_deal_quote(create_deal_request, idempotency_key, x_request_id)


@router.get(
    "/api/v1/deals/pending",
    responses={
        200: {"model": PendingDealsResponse, "description": "Список незавершённых сделок успешно получен"},
        400: {"model": ErrorResponse, "description": "Некорректные параметры пагинации"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации query-параметров"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    tags=["Deals"],
    summary="Получение списка незавершённых сделок",
    response_model_by_alias=True,
)
async def get_pending_deals(
    limit: int = Query(20, description="Количество возвращаемых записей (для пагинации)", alias="limit", ge=1, le=100),
    offset: int = Query(0, description="Смещение от начала списка (для пагинации)", alias="offset", ge=0),
    x_request_id: str = Header(None, description="Идентификатор корреляции для сквозного логирования"),
) -> PendingDealsResponse:
    """Возвращает список всех активных сделок, находящихся в статусе PENDING. """
    return BaseDealsApi.subclasses[0]().get_pending_deals(limit, offset, x_request_id)


@router.patch(
    "/api/v1/deals/{deal_id}",
    responses={
        200: {"model": DealStatusResponse, "description": "Результат сделки успешно зафиксирован в системе"},
        400: {"model": ErrorResponse, "description": "Срок действия предложения истек (Deal Expired)"},
        404: {"model": ErrorResponse, "description": "Сделка с указанным deal_id не найдена"},
        409: {"model": ErrorResponse, "description": "Конфликт состояния (сделка уже была закрыта ранее)"},
        422: {"model": ValidationErrorResponse, "description": "Ошибка валидации входных данных (неверный UUID или action)"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
    tags=["Deals"],
    summary="Подтверждение или отклонение обмена валют",
    response_model_by_alias=True,
)
async def update_deal_status(
    deal_id: str = Path(..., description="Уникальный идентификатор возможной сделки"),
    update_deal_request: UpdateDealRequest = Body(None, description=""),
    idempotency_key: str = Header(None, description="Уникальный ключ идемпотентности запроса"),
) -> DealStatusResponse:
    """Переводит ранее созданную возможную сделку из статуса PENDING в итоговый статус CONFIRMED или REJECTED. """
    return BaseDealsApi.subclasses[0]().update_deal_status(deal_id, update_deal_request, idempotency_key)
