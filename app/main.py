from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
import logging.config
from app.core.logging import LOG_CONFIG

from app.api.health import router as health_router
from app.api.router import api_router
from app.background.bank_client import NBRBClient, NBRBClientAdapter
from app.background.scheduler import create_scheduler, run_currency_sync_job
from app.config import get_nbrb_settings
from app.core.database import AsyncSessionLocal, dispose_engine
from app.core.exception_handlers import setup_exception_handlers
from app.services.currency_sync_service import CurrencySyncService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    nbrb_settings = get_nbrb_settings()
    nbrb_client = NBRBClient(nbrb_settings)
    nbrb_adapter = NBRBClientAdapter(nbrb_client)
    currency_sync_service = CurrencySyncService(
        session_factory=AsyncSessionLocal,
        adapter=nbrb_adapter,
    )
    app.state.nbrb_settings = nbrb_settings
    app.state.nbrb_client = nbrb_client
    app.state.nbrb_adapter = nbrb_adapter
    app.state.currency_sync_service = currency_sync_service

    scheduler: AsyncIOScheduler | None = None

    try:
        await run_currency_sync_job(currency_sync_service)
        scheduler = create_scheduler(currency_sync_service)
        scheduler.start()
        yield
    finally:
        if scheduler is not None and scheduler.running:
            scheduler.shutdown(wait=True)
        await nbrb_client.aclose()
        await dispose_engine()


app = FastAPI(
    title="Currency Exchange Service",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)


setup_exception_handlers(app)
logging.config.dictConfig(LOG_CONFIG)
app.mount("/static-openapi", StaticFiles(directory="openapi"), name="static-openapi")


@app.get("/swagger-ui", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/static-openapi/openapi.json",
        title="Currency Exchange Service — Swagger UI",
    )


app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")
