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


class NBRBClientException(Error):
    pass


class NBRBNetworkException(NBRBClientException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="NBRB_NETWORK_ERROR",
            message="Не удалось выполнить запрос к API НБ РБ.",
            details={"reason": reason},
        )
        self.reason = reason


class NBRBAPIException(NBRBClientException):
    def __init__(self, status_code: int, response_body: str) -> None:
        super().__init__(
            code="NBRB_API_ERROR",
            message=f"API НБ РБ вернул HTTP {status_code}.",
            details={
                "status_code": status_code,
                "response_body": response_body[:500],
            },
        )
        self.status_code = status_code
        self.response_body = response_body


class NBRBResponseValidationException(NBRBClientException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="NBRB_RESPONSE_VALIDATION_ERROR",
            message="Ответ API НБ РБ не соответствует ожидаемой схеме.",
            details={"reason": reason},
        )
        self.reason = reason


class ReportValidationError(Error):
    pass
