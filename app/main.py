from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api.health import router as health_router
from app.api.router import api_router

app = FastAPI(
    title="Currency Exchange Service",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/static-openapi", StaticFiles(directory="openapi"), name="static-openapi")

@app.get("/swagger-ui", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/static-openapi/openapi.json",
        title="Currency Exchange Service — Swagger UI",
    )

app.include_router(health_router)
app.include_router(api_router, prefix="/api/v1")