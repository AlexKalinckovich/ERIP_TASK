from fastapi import APIRouter

from app.api.v1 import deals, reports

api_router = APIRouter()

api_router.include_router(reports.router)
api_router.include_router(deals.router)
