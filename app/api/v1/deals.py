from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    status,
)

from app.api.dependencies import IdempotencyKeyDep, get_deal_service
from app.schemas.deal import (
    CreateDealRequest,
    DealQuoteResponse,
    DealStatusResponse,
    PendingDealsResponse,
    UpdateDealRequest,
)
from app.schemas.errors import ErrorResponse, ValidationErrorResponse
from app.services.common_validator import parse_uuid_or_raise
from app.services.deal_service import DealService

router = APIRouter(prefix="/deals")

DealServiceDep = Annotated[DealService, Depends(get_deal_service)]


@router.post(
    "",
    responses={
        201: {
            "model": DealQuoteResponse,
            "description": "Предварительная сделка успешно создана",
        },
        400: {
            "model": ErrorResponse,
            "description": "Ошибка бизнес-логики (одинаковые валюты, отсутствие курса)",
        },
        409: {
            "model": ErrorResponse,
            "description": "Конфликт ключа идемпотентности",
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Ошибка валидации входных данных (Pydantic Validation Error)",
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
        },
        503: {
            "model": ErrorResponse,
            "description": "Сервис или База Данных временно недоступны",
        },
    },
    tags=["Deals"],
    summary="Создание предварительной сделки на обмен валют",
    response_model=DealQuoteResponse,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=True,
)
async def create_deal_quote(
    response: Response,
    service: DealServiceDep,
    idempotency_key: IdempotencyKeyDep,
    create_deal_request: Annotated[
        CreateDealRequest | None,
        Body(description=""),
    ] = None,
    x_request_id: str = Header(
        None,
        description="Идентификатор корреляции для сквозного логирования",
    ),
) -> DealQuoteResponse:
    if create_deal_request is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Request body is required",
        )

    quote = await service.create_deal(
        request=create_deal_request,
        idempotency_key=idempotency_key,
    )

    response.headers["Location"] = f"/api/v1/deals/{quote.deal_id}"

    return quote


@router.get(
    "/pending",
    responses={
        200: {
            "model": PendingDealsResponse,
            "description": "Список незавершённых сделок успешно получен",
        },
        400: {
            "model": ErrorResponse,
            "description": "Некорректные параметры пагинации",
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Ошибка валидации query-параметров",
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
        },
    },
    tags=["Deals"],
    summary="Получение списка незавершённых сделок",
    response_model=PendingDealsResponse,
    response_model_by_alias=True,
)
async def get_pending_deals(
    service: DealServiceDep,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            alias="limit",
            description="Количество возвращаемых записей (для пагинации)",
        ),
    ] = 20,
    offset: Annotated[
        int,
        Query(
            ge=0,
            alias="offset",
            description="Смещение от начала списка (для пагинации)",
        ),
    ] = 0,
    x_request_id: str = Header(
        None,
        description="Идентификатор корреляции для сквозного логирования",
    ),
) -> PendingDealsResponse:
    return await service.get_pending_deals(
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{deal_id}",
    responses={
        200: {
            "model": DealStatusResponse,
            "description": "Результат сделки успешно зафиксирован в системе",
        },
        400: {
            "model": ErrorResponse,
            "description": "Срок действия предложения истек (Deal Expired)",
        },
        404: {
            "model": ErrorResponse,
            "description": "Сделка с указанным deal_id не найдена",
        },
        409: {
            "model": ErrorResponse,
            "description": "Конфликт состояния сделки или ключа идемпотентности",
        },
        422: {
            "model": ValidationErrorResponse,
            "description": "Ошибка валидации входных данных (неверный UUID или action)",
        },
        500: {
            "model": ErrorResponse,
            "description": "Внутренняя ошибка сервера",
        },
    },
    tags=["Deals"],
    summary="Подтверждение или отклонение обмена валют",
    response_model=DealStatusResponse,
    response_model_by_alias=True,
)
async def update_deal_status(
    service: DealServiceDep,
    idempotency_key: IdempotencyKeyDep,
    deal_id: str = Path(
        ...,
        description="Уникальный идентификатор возможной сделки",
    ),
    update_deal_request: Annotated[
        UpdateDealRequest | None,
        Body(description=""),
    ] = None,
) -> DealStatusResponse:
    if update_deal_request is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Request body is required",
        )

    deal_id_value = parse_uuid_or_raise(
        deal_id,
        field="deal_id",
        version=4,
    )

    return await service.update_deal_status(
        deal_id=deal_id_value,
        request=update_deal_request,
        idempotency_key=idempotency_key,
    )
