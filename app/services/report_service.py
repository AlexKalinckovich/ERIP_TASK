from datetime import datetime

from app.repositories import DealRepository
from app.schemas.report import SummaryReportResponse
from app.services.report_validator import ReportValidator


class ReportService:
    def __init__(self, validator: ReportValidator, deal_repository: DealRepository) -> None:
        self._validator = validator
        self._deal_repository = deal_repository

    async def get_deals_summary_report(
        self,
        date_from: datetime,
        date_to: datetime,
        currency: str | None = None,
    ) -> SummaryReportResponse:
        self._validator.validate_summary_request(date_from, date_to)
        reports = await self._deal_repository.get_summary_report(date_from, date_to, currency)
        items = list(reports)
        return SummaryReportResponse(
            date_from=date_from,
            date_to=date_to,
            items=items,
        )