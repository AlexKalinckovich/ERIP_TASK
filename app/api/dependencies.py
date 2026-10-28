from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.background.bank_client import NBRBClient, NBRBClientAdapter
from app.config import NBRBSettings
from app.core.database import get_db
from app.repositories.deal import DealRepository
from app.repositories.exchange_rate import ExchangeRateRepository
from app.services.common_validator import parse_uuid_or_raise
from app.services.currency_sync_service import CurrencySyncService
from app.services.deal_service import DealService
from app.services.deal_validator import DealValidator
from app.services.report_service import ReportService
from app.services.report_validator import ReportValidator

DatabaseSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_idempotency_key(
    idempotency_key: Annotated[
        str | None,
        Header(
            alias="Idempotency-Key",
            description="Уникальный ключ идемпотентности запроса (UUID v4)",
        ),
    ] = None,
) -> UUID | None:
    if idempotency_key is None:
        return None

    value = parse_uuid_or_raise(
        idempotency_key,
        field="Idempotency-Key",
        location="header",
        version=4,
    )

    return value


IdempotencyKeyDep = Annotated[UUID | None, Depends(get_idempotency_key)]


def get_nbrb_settings(request: Request) -> NBRBSettings:
    return request.app.state.nbrb_settings


def get_nbrb_client(request: Request) -> NBRBClient:
    return request.app.state.nbrb_client


def get_nbrb_adapter(request: Request) -> NBRBClientAdapter:
    return request.app.state.nbrb_adapter


NBRBSettingsDep = Annotated[NBRBSettings, Depends(get_nbrb_settings)]
NBRBClientDep = Annotated[NBRBClient, Depends(get_nbrb_client)]
NBRBClientAdapterDep = Annotated[
    NBRBClientAdapter,
    Depends(get_nbrb_adapter),
]


def get_currency_sync_service(request: Request) -> CurrencySyncService:
    return request.app.state.currency_sync_service


CurrencySyncServiceDep = Annotated[
    CurrencySyncService,
    Depends(get_currency_sync_service),
]


def get_exchange_rate_repository(
    session: DatabaseSessionDep,
) -> ExchangeRateRepository:
    return ExchangeRateRepository(session)


def get_deal_repository(
    session: DatabaseSessionDep,
) -> DealRepository:
    return DealRepository(session)


ExchangeRateRepositoryDep = Annotated[
    ExchangeRateRepository,
    Depends(get_exchange_rate_repository),
]
DealRepositoryDep = Annotated[
    DealRepository,
    Depends(get_deal_repository),
]


def get_deal_validator() -> DealValidator:
    return DealValidator()


def get_deal_service(
    validator: Annotated[DealValidator, Depends(get_deal_validator)],
    rate_repository: ExchangeRateRepositoryDep,
    deal_repository: DealRepositoryDep,
) -> DealService:
    return DealService(
        validator=validator,
        rate_repository=rate_repository,
        deal_repository=deal_repository,
    )


def get_report_validator() -> ReportValidator:
    return ReportValidator()


def get_report_service(
    validator: Annotated[ReportValidator, Depends(get_report_validator)],
    deal_repository: DealRepositoryDep,
) -> ReportService:
    return ReportService(validator=validator, deal_repository=deal_repository)
