from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router

app = FastAPI(
    title="Currency Exchange Service",
    version="0.1.0",
    docs_url=None,       # отключаем встроенный /docs
    redoc_url=None,
    openapi_url=None,    # отключаем встроенный /openapi.json
    openapi_version="3.0.3",
)

# Статика с openapi.yaml/json
app.mount("/static-openapi", StaticFiles(directory="openapi"), name="static-openapi")

# Свой Swagger UI со статическим OpenAPI
@app.get("/swagger-ui", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/static-openapi/openapi.json",
        title="Currency Exchange Service — Swagger UI",
    )

app.include_router(api_router, prefix="/api/v1")