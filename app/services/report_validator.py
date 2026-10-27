from datetime import UTC, datetime

from app.core.exceptions import ReportValidationError


class ReportValidator:
    def validate_summary_request(
        self,
        date_from: datetime,
        date_to: datetime,
    ) -> None:
        normalized_from = (
            date_from
            if date_from.tzinfo is not None
            else date_from.replace(tzinfo=UTC)
        )
        normalized_to = (
            date_to
            if date_to.tzinfo is not None
            else date_to.replace(tzinfo=UTC)
        )

        if normalized_from > normalized_to:
            raise ReportValidationError(
                code="INVALID_DATE_RANGE",
                message="Начало интервала не может быть позже конца интервала.",
                details={
                    "date_from": normalized_from.isoformat(),
                    "date_to": normalized_to.isoformat(),
                },
            )
