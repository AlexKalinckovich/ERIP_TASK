import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.background.bank_client import NBRBClientAdapter
from app.repositories.deal import DealRepository
from app.repositories.exchange_rate import ExchangeRateRepository, RateRow

logger = logging.getLogger(__name__)


class CurrencySyncService:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        adapter: NBRBClientAdapter,
    ) -> None:
        self._session_factory = session_factory
        self._adapter = adapter

    async def sync_rates_and_expire_deals(self) -> None:
        logger.info("Запуск фоновой задачи синхронизации курсов валют.")
        today = datetime.now(UTC).date()

        async with self._session_factory() as session:
            try:
                rate_repository = ExchangeRateRepository(session)
                deal_repository = DealRepository(session)

                if await rate_repository.has_rates_for_date(today):
                    logger.info(
                        "Курсы валют за текущую дату (%s) уже загружены.",
                        today,
                    )
                else:
                    rates = await self._adapter.get_rates(periodicity=0)
                    if rates:
                        formatted_rates: list[RateRow] = [
                            {
                                "rate_date": rate.date.date(),
                                "currency_code": rate.cur_abbreviation,
                                "scale": rate.cur_scale,
                                "official_rate": rate.cur_official_rate,
                            }
                            for rate in rates
                        ]
                        await rate_repository.upsert_rates(formatted_rates)
                        logger.info(
                            "Сохранено %s курсов валют.",
                            len(formatted_rates),
                        )
                    else:
                        logger.warning(
                            "Курсы валют от НБ РБ не получены. "
                            "Используются старые данные.",
                        )

                expired_count = await deal_repository.expire_outdated_deals()
                if expired_count:
                    logger.info(
                        "Переведено в EXPIRED %s просроченных сделок.",
                        expired_count,
                    )

                await session.commit()
            except Exception:
                await session.rollback()
                logger.exception(
                    "Ошибка в процессе синхронизации курсов валют.",
                )
                raise
