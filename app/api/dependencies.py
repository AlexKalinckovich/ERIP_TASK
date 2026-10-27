from typing import Annotated

from fastapi import Depends

from app.services.deal_service import DealService
from app.services.deal_validator import DealValidator
from app.services.report_service import ReportService
from app.services.report_validator import ReportValidator


def get_deal_validator() -> DealValidator:
    return DealValidator()


def get_deal_service(
    validator: Annotated[DealValidator, Depends(get_deal_validator)],
) -> DealService:
    return DealService(validator=validator)


def get_report_validator() -> ReportValidator:
    return ReportValidator()


def get_report_service(
    validator: Annotated[ReportValidator, Depends(get_report_validator)],
) -> ReportService:
    return ReportService(validator=validator)
