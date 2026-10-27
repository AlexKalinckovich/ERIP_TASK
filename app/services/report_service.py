from datetime import datetime

from app.schemas.report import SummaryReportResponse
from app.services.report_validator import ReportValidator


class ReportService:
    def __init__(self, validator: ReportValidator) -> None:
        self._validator = validator

    async def get_deals_summary_report(
        self,
        date_from: datetime,
        date_to: datetime,
        currency: str | None = None,
    ) -> SummaryReportResponse:
        self._validator.validate_summary_request(date_from, date_to)
        _ = currency

        return SummaryReportResponse(
            date_from=date_from,
            date_to=date_to,
            items=[],
        )
