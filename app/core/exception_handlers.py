from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    DealValidationError,
    Error,
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

async def deal_validation_exception_handler(
    _request: Request,
    exc: DealValidationError,
) -> JSONResponse:
    return _error_response(status.HTTP_400_BAD_REQUEST, exc)

async def report_validation_exception_handler(
    _request: Request,
    exc: ReportValidationError,
) -> JSONResponse:
    return _error_response(status.HTTP_400_BAD_REQUEST, exc)

async def invalid_uuid_exception_handler(
    _request: Request,
    exc: InvalidUUIDError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=ValidationErrorResponse(
            detail=[
                ValidationErrorItem(
                    loc=["path", exc.field],
                    msg=exc.message,
                    type="uuid_parsing",
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
        InvalidUUIDError,
        invalid_uuid_exception_handler,
    )
