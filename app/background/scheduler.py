from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.currency_sync_service import CurrencySyncService


async def run_currency_sync_job(service: CurrencySyncService) -> None:
    await service.sync_rates_and_expire_deals()


def create_scheduler(service: CurrencySyncService) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        run_currency_sync_job,
        trigger="cron",
        args=[service],
        hour=10,
        minute=0,
        id="currency-sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    return scheduler
