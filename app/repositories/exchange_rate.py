from collections.abc import Sequence
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import exists, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.rate import ExchangeRate


class RateRow(TypedDict):
    rate_date: date
    currency_code: str
    scale: int
    official_rate: Decimal


class ExchangeRateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_rate_by_currency(
        self,
        currency_code: str,
        rate_date: date,
    ) -> ExchangeRate | None:
        stmt = select(ExchangeRate).where(
            ExchangeRate.currency_code == currency_code.upper(),
            ExchangeRate.rate_date == rate_date,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_rates_by_currencies(
        self,
        currency_codes: Sequence[str],
        rate_date: date,
    ) -> Sequence[ExchangeRate]:
        normalized_codes = [code.upper() for code in currency_codes]
        stmt = select(ExchangeRate).where(
            ExchangeRate.currency_code.in_(normalized_codes),
            ExchangeRate.rate_date == rate_date,
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def has_rates_for_date(self, target_date: date) -> bool:
        stmt = select(exists().where(ExchangeRate.rate_date == target_date))
        return bool(await self._session.scalar(stmt))

    async def upsert_rates(self, rates_data: list[RateRow]) -> None:
        if not rates_data:
            return

        stmt = insert(ExchangeRate).values(rates_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                ExchangeRate.rate_date,
                ExchangeRate.currency_code,
            ],
            set_={
                "scale": stmt.excluded.scale,
                "official_rate": stmt.excluded.official_rate,
                "created_at": datetime.now(UTC),
            },
        )
        await self._session.execute(stmt)
