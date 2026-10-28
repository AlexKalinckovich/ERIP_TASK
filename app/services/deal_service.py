import logging
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    DealExpiredError,
    DealNotFoundError,
    DealProcessingError,
    DealStateConflictError,
    DealValidationError,
    IdempotencyConflictError,
)
from app.db.models.deal import Deal
from app.db.models.deal_status_idempotency import DealStatusIdempotency
from app.db.models.rate import ExchangeRate
from app.mapper.deal_mapper import map_deal_to_pending_item
from app.repositories.deal import DealRepository
from app.repositories.exchange_rate import ExchangeRateRepository
from app.schemas.deal import (
    CreateDealRequest,
    DealAction,
    DealFinalStatus,
    DealQuoteResponse,
    DealStatus,
    DealStatusResponse,
    PendingDealsResponse,
    UpdateDealRequest
)
from app.services.deal_validator import DealValidator

_BYN = "BYN"
_RATE_QUANTUM = Decimal("0.0001")
_AMOUNT_QUANTUM = Decimal("0.01")
_MAX_AMOUNT = Decimal("100000.00")

logger = logging.getLogger(__name__)


class DealService:
    def __init__(
        self,
        validator: DealValidator,
        rate_repository: ExchangeRateRepository,
        deal_repository: DealRepository,
    ) -> None:
        self._validator = validator
        self._rate_repository = rate_repository
        self._deal_repository = deal_repository

    async def create_deal(
        self,
        request: CreateDealRequest,
        idempotency_key: UUID | None = None,
    ) -> DealQuoteResponse:
        if idempotency_key is not None:
            existing_deal = await self._deal_repository.get_by_idempotency_key(
                idempotency_key,
            )
            if existing_deal is not None:
                return self._resolve_idempotent(
                    deal=existing_deal,
                    request=request,
                    idempotency_key=idempotency_key,
                )

        self._validator.validate_create_request(request)
        now = datetime.now(UTC)
        rate_date = now.date()
        exchange_rate = await self._calculate_exchange_rate(
            source_currency=request.source_currency,
            target_currency=request.target_currency,
            rate_date=rate_date,
        )
        target_amount = (request.amount * exchange_rate).quantize(
            _AMOUNT_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
        if target_amount <= 0:
            raise DealValidationError(
                code="TARGET_AMOUNT_TOO_SMALL",
                message="Рассчитанная сумма в целевой валюте слишком мала.",
            )

        try:
            deal = await self._deal_repository.create_deal(
                deal_id=uuid4(),
                source_currency=request.source_currency,
                target_currency=request.target_currency,
                source_amount=request.amount,
                target_amount=min(target_amount, _MAX_AMOUNT),
                exchange_rate=exchange_rate,
                idempotency_key=idempotency_key,
            )
            await self._deal_repository.commit()
        except IntegrityError:
            logger.warning("integrity_error_during_creation", exc_info=True)
            await self._deal_repository.rollback()
            if idempotency_key is None:
                raise
            existing_deal = await self._deal_repository.get_by_idempotency_key(
                idempotency_key,
            )
            if existing_deal is None:
                raise
            return self._resolve_idempotent(
                deal=existing_deal,
                request=request,
                idempotency_key=idempotency_key,
            )

        return DealQuoteResponse.model_validate(deal)

    @staticmethod
    def _resolve_idempotent(
        deal: Deal,
        request: CreateDealRequest,
        idempotency_key: UUID,
    ) -> DealQuoteResponse:
        if (
            deal.source_currency != request.source_currency
            or deal.target_currency != request.target_currency
            or deal.source_amount != request.amount
        ):
            raise IdempotencyConflictError(
                idempotency_key=idempotency_key,
                deal_id=deal.deal_id,
            )

        return DealQuoteResponse.model_validate(deal)

    async def _calculate_exchange_rate(
        self,
        source_currency: str,
        target_currency: str,
        rate_date: date,
    ) -> Decimal:
        source_rate, target_rate = await self._get_rates(
            source_currency=source_currency,
            target_currency=target_currency,
            rate_date=rate_date,
        )
        exchange_rate = (
            self._to_byn_rate(source_rate) / self._to_byn_rate(target_rate)
        ).quantize(
            _RATE_QUANTUM,
            rounding=ROUND_HALF_UP,
        )
        if exchange_rate <= 0:
            raise DealValidationError(
                code="INVALID_EXCHANGE_RATE",
                message="Рассчитанный курс обмена некорректен.",
            )
        return exchange_rate

    async def _get_rates(
        self,
        source_currency: str,
        target_currency: str,
        rate_date: date,
    ) -> tuple[ExchangeRate | None, ExchangeRate | None]:
        if source_currency == _BYN:
            target_rate = await self._rate_repository.get_rate_by_currency(
                target_currency,
                rate_date,
            )
            self._ensure_rate_exists(target_rate, target_currency, rate_date)
            return None, target_rate

        if target_currency == _BYN:
            source_rate = await self._rate_repository.get_rate_by_currency(
                source_currency,
                rate_date,
            )
            self._ensure_rate_exists(source_rate, source_currency, rate_date)
            return source_rate, None

        rates = await self._rate_repository.get_rates_by_currencies(
            [source_currency, target_currency],
            rate_date,
        )
        rates_by_code = {rate.currency_code: rate for rate in rates}
        source_rate = rates_by_code.get(source_currency)
        target_rate = rates_by_code.get(target_currency)
        self._ensure_rate_exists(source_rate, source_currency, rate_date)
        self._ensure_rate_exists(target_rate, target_currency, rate_date)
        return source_rate, target_rate

    @staticmethod
    def _to_byn_rate(rate: ExchangeRate | None) -> Decimal:
        if rate is None:
            return Decimal(1)
        return rate.official_rate / Decimal(rate.scale)

    @staticmethod
    def _ensure_rate_exists(
        rate: ExchangeRate | None,
        currency_code: str,
        rate_date: date,
    ) -> None:
        if rate is None:
            raise DealValidationError(
                code="EXCHANGE_RATE_NOT_FOUND",
                message="Курс валюты не найден на текущую дату.",
                details={
                    "currency": currency_code,
                    "rate_date": rate_date.isoformat(),
                },
            )

    async def get_pending_deals(
        self,
        limit: int,
        offset: int,
    ) -> PendingDealsResponse:
        deals = await self._deal_repository.get_pending_deals(limit, offset)

        pending_items = [map_deal_to_pending_item(deal) for deal in deals]

        return PendingDealsResponse(
            total=len(pending_items),
            limit=limit,
            offset=offset,
            items= pending_items,
        )

    async def update_deal_status(
        self,
        deal_id: UUID,
        request: UpdateDealRequest,
        idempotency_key: UUID | None = None,
    ) -> DealStatusResponse:
        target_status = (
            DealFinalStatus.CONFIRMED
            if request.action == DealAction.CONFIRM
            else DealFinalStatus.REJECTED
        )
        now = datetime.now(UTC)

        if idempotency_key is not None:
            existing_idempotency = await self._deal_repository.get_status_idempotency(
                idempotency_key,
            )

            if existing_idempotency is not None:
                return self._resolve_status_idempotent_or_raise(
                    record=existing_idempotency,
                    deal_id=deal_id,
                    action=request.action,
                    idempotency_key=idempotency_key,
                )

        try:
            updated_deal = await self._deal_repository.update_status_if_pending(
                deal_id=deal_id,
                new_status=target_status,
                now=now,
            )
            if updated_deal is not None:
                if idempotency_key is not None:
                    await self._deal_repository.create_status_idempotency(
                        idempotency_key=idempotency_key,
                        deal_id=deal_id,
                        action=request.action.value,
                        status=target_status.value,
                        updated_at=updated_deal.updated_at,
                    )
                await self._deal_repository.commit()
                return DealStatusResponse(
                    deal_id=updated_deal.deal_id,
                    status=target_status,
                    updated_at=updated_deal.updated_at,
                )
            logger.warning("deal_status_update_failed_no_rows_updated")
            return await self._diagnose_status_update_failure(
                deal_id=deal_id,
                action=request.action,
                idempotency_key=idempotency_key,
            )
        except IntegrityError:
            logger.warning("integrity_error_during_status_update", exc_info=True)
            await self._deal_repository.rollback()
            if idempotency_key is None:
                raise
            existing_idempotency = await self._deal_repository.get_status_idempotency(
                idempotency_key,
            )
            if existing_idempotency is None:
                raise
            return self._resolve_status_idempotent_or_raise(
                record=existing_idempotency,
                deal_id=deal_id,
                action=request.action,
                idempotency_key=idempotency_key,
            )

    async def _diagnose_status_update_failure(
        self,
        deal_id: UUID,
        action: DealAction,
        idempotency_key: UUID | None,
    ) -> DealStatusResponse:
        existing_deal = await self._deal_repository.get_by_id(deal_id)

        if existing_deal is None:
            raise DealNotFoundError(deal_id=deal_id)

        if idempotency_key is not None:
            existing_idempotency = await self._deal_repository.get_status_idempotency(
                idempotency_key,
            )
            if existing_idempotency is not None:
                return self._resolve_status_idempotent_or_raise(
                    record=existing_idempotency,
                    deal_id=deal_id,
                    action=action,
                    idempotency_key=idempotency_key,
                )

        if existing_deal.status == DealStatus.EXPIRED.value:
            raise DealExpiredError(deal_id=deal_id)

        if existing_deal.status != DealStatus.PENDING.value:
            raise DealStateConflictError(
                deal_id=deal_id,
                status=existing_deal.status,
            )

        raise DealProcessingError(deal_id=deal_id)

    @staticmethod
    def _resolve_status_idempotent_or_raise(
        record: DealStatusIdempotency,
        deal_id: UUID,
        action: DealAction,
        idempotency_key: UUID,
    ) -> DealStatusResponse:
        if record.deal_id != deal_id or record.action != action.value:
            raise IdempotencyConflictError(
                idempotency_key=idempotency_key,
                deal_id=record.deal_id,
            )

        return DealStatusResponse(
            deal_id=record.deal_id,
            status=DealFinalStatus(record.status),
            updated_at=record.updated_at,
        )
