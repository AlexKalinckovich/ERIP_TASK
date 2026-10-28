from datetime import datetime, timezone
from decimal import Decimal
from typing import Sequence
from uuid import UUID

from sqlalchemy import func, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update, union_all, literal, cast, Numeric

from app.db.models.deal import Deal
from app.db.models.deal_status_idempotency import DealStatusIdempotency
from app.mapper.report_mapper import map_db_row_to_summary_report_item
from app.schemas.deal import DealStatus
from app.schemas.report import SummaryReportItem


class DealRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_summary_report(
            self,
            date_from: datetime,
            date_to: datetime,
            currency: str | None = None,
    ) -> Sequence[SummaryReportItem]:
        sql_query = text("""
            SELECT currency, total_received, total_given, deal_count
            FROM get_deal_summary_report(:date_from, :date_to, :currency)
        """)

        result = await self._session.execute(
            sql_query,
            {
                "date_from": date_from,
                "date_to": date_to,
                "currency": currency.upper() if currency else None,
            }
        )

        rows = result.mappings().all()

        return [map_db_row_to_summary_report_item(row) for row in rows]

    async def get_pending_deals(self, limit: int, offset: int) -> Sequence[Deal]:
        stmt = (
            select(Deal)
            .where(
                Deal.status == DealStatus.PENDING.value,
            )
            .order_by(Deal.created_at)
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)

        deals = result.scalars().all()

        return deals

    async def get_by_idempotency_key(
        self,
        idempotency_key: UUID,
    ) -> Deal | None:
        stmt = select(Deal).where(Deal.idempotency_key == idempotency_key)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, deal_id: UUID) -> Deal | None:
        stmt = select(Deal).where(Deal.deal_id == deal_id)

        result = await self._session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_status_idempotency(
        self,
        idempotency_key: UUID,
    ) -> DealStatusIdempotency | None:
        stmt = select(DealStatusIdempotency).where(
            DealStatusIdempotency.idempotency_key == idempotency_key,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_status_idempotency(
        self,
        *,
        idempotency_key: UUID,
        deal_id: UUID,
        action: str,
        status: str,
        updated_at: datetime,
    ) -> DealStatusIdempotency:
        record = DealStatusIdempotency(
            idempotency_key=idempotency_key,
            deal_id=deal_id,
            action=action,
            status=status,
            updated_at=updated_at,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def create_deal(
        self,
        *,
        deal_id: UUID,
        source_currency: str,
        target_currency: str,
        source_amount: Decimal,
        target_amount: Decimal,
        exchange_rate: Decimal,
            idempotency_key: UUID | None = None,
    ) -> Deal:
        deal = Deal(
            deal_id=deal_id,
            source_currency=source_currency.upper(),
            target_currency=target_currency.upper(),
            source_amount=source_amount,
            target_amount=target_amount,
            exchange_rate=exchange_rate,
            status=DealStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        self._session.add(deal)
        await self._session.flush()
        await self._session.refresh(deal)
        return deal

    async def update_status_if_pending(
        self,
        deal_id: UUID,
        new_status: DealStatus,
        now: datetime,
    ) -> Deal | None:
        stmt = (
            update(Deal)
            .where(
                Deal.deal_id == deal_id,
                Deal.status == DealStatus.PENDING.value,
            )
            .values(
                status=new_status.value,
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
            .returning(Deal)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def expire_outdated_deals(self) -> int:
        stmt = (
            update(Deal)
            .where(
                Deal.status == DealStatus.PENDING.value
            )
            .values(
                status=DealStatus.EXPIRED.value,
                updated_at=func.now(),
            )
        )
        result = await self._session.execute(stmt)
        return result.rowcount or 0

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
