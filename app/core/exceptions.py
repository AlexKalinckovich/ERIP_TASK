from abc import ABC
from typing import Any
from uuid import UUID


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


class IdempotencyConflictError(Error):
    def __init__(self, idempotency_key: UUID, deal_id: UUID) -> None:
        super().__init__(
            code="IDEMPOTENCY_KEY_CONFLICT",
            message="Ключ идемпотентности уже использован для другого запроса.",
            details={
                "idempotency_key": str(idempotency_key),
                "deal_id": str(deal_id),
            },
        )


class DealNotFoundError(Error):
    def __init__(self, deal_id: UUID) -> None:
        super().__init__(
            code="DEAL_NOT_FOUND",
            message="Сделка с указанным идентификатором не найдена.",
            details={"deal_id": str(deal_id)},
        )


class DealExpiredError(Error):
    def __init__(self, deal_id: UUID) -> None:
        super().__init__(
            code="DEAL_EXPIRED",
            message="Срок действия предложения истек.",
            details={"deal_id": str(deal_id)},
        )


class DealStateConflictError(Error):
    def __init__(self, deal_id: UUID, status: str) -> None:
        super().__init__(
            code="DEAL_STATE_CONFLICT",
            message="Сделка уже находится в терминальном статусе.",
            details={"deal_id": str(deal_id), "status": status},
        )


class DealProcessingError(Error):
    def __init__(self, deal_id: UUID) -> None:
        super().__init__(
            code="DEAL_PROCESSING_ERROR",
            message="Не удалось обновить статус сделки.",
            details={"deal_id": str(deal_id)},
        )


class InvalidUUIDError(Error):
    def __init__(
        self,
        field: str = "id",
        message: str = "Некорректный UUID.",
        location: str = "path",
        error_type: str = "uuid_parsing",
    ) -> None:
        super().__init__(
            code="INVALID_UUID",
            message=message,
            details={"field": field},
        )
        self.field = field
        self.location = location
        self.error_type = error_type


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
