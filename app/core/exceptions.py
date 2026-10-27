from abc import ABC
from typing import Any


class Error(Exception, ABC):
    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


class DealValidationError(Error):
    pass


class InvalidUUIDError(Error):
    def __init__(self, field: str = "id") -> None:
        super().__init__(
            code="INVALID_UUID",
            message="Некорректный UUID.",
            details={"field": field},
        )
        self.field = field


class ReportValidationError(Error):
    pass
