from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DealExpiredError,
    DealNotFoundError,
    DealProcessingError,
    DealStateConflictError,
    DealValidationError,
    Error,
    IdempotencyConflictError,
    InvalidUUIDError,
    ReportValidationError,
)
from app.schemas.errors import (
    ErrorResponse,
    ValidationErrorItem,
    ValidationErrorResponse,
)


def _error_response(status_code: int, exc: Error) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ).model_dump(),
    )


def deal_validation_exception_handler(
    _request: Request,
    exc: DealValidationError,
) -> JSONResponse:
    return _error_response(status.HTTP_400_BAD_REQUEST, exc)


def report_validation_exception_handler(
    _request: Request,
    exc: ReportValidationError,
) -> JSONResponse:
    return _error_response(status.HTTP_400_BAD_REQUEST, exc)


def idempotency_conflict_exception_handler(
    _request: Request,
    exc: IdempotencyConflictError,
) -> JSONResponse:
    return _error_response(status.HTTP_409_CONFLICT, exc)


def deal_not_found_exception_handler(
    _request: Request,
    exc: DealNotFoundError,
) -> JSONResponse:
    return _error_response(status.HTTP_404_NOT_FOUND, exc)


def deal_expired_exception_handler(
    _request: Request,
    exc: DealExpiredError,
) -> JSONResponse:
    return _error_response(status.HTTP_400_BAD_REQUEST, exc)


def deal_state_conflict_exception_handler(
    _request: Request,
    exc: DealStateConflictError,
) -> JSONResponse:
    return _error_response(status.HTTP_409_CONFLICT, exc)


def deal_processing_exception_handler(
    _request: Request,
    exc: DealProcessingError,
) -> JSONResponse:
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, exc)


def invalid_uuid_exception_handler(
    _request: Request,
    exc: InvalidUUIDError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ValidationErrorResponse(
            detail=[
                ValidationErrorItem(
                    loc=[exc.location, exc.field],
                    msg=exc.message,
                    type=exc.error_type,
                )
            ]
        ).model_dump(),
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DealValidationError,
        deal_validation_exception_handler,
    )
    app.add_exception_handler(
        ReportValidationError,
        report_validation_exception_handler,
    )
    app.add_exception_handler(
        IdempotencyConflictError,
        idempotency_conflict_exception_handler,
    )
    app.add_exception_handler(
        DealNotFoundError,
        deal_not_found_exception_handler,
    )
    app.add_exception_handler(
        DealExpiredError,
        deal_expired_exception_handler,
    )
    app.add_exception_handler(
        DealStateConflictError,
        deal_state_conflict_exception_handler,
    )
    app.add_exception_handler(
        DealProcessingError,
        deal_processing_exception_handler,
    )
    app.add_exception_handler(
        InvalidUUIDError,
        invalid_uuid_exception_handler,
    )
