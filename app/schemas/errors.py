from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(
        ...,
        description="Машиночитаемый код ошибки",
        examples=["SAME_CURRENCY_NOT_ALLOWED"],
    )
    message: str = Field(
        ...,
        description="Человекочитаемое сообщение об ошибке",
        examples=["Исходная и целевая валюты не могут совпадать."],
    )
    details: dict[str, Any] | None = Field(
        default=None,
        description="Опциональные структурированные детали (например, имя поля)",
    )


class ValidationErrorItem(BaseModel):
    loc: list[str | int] = Field(
        ...,
        description="Путь до проблемного поля в теле запроса",
        examples=[["body", "amount"]],
    )
    msg: str = Field(
        ...,
        description="Человекочитаемое сообщение",
        examples=["Input should be greater than 0"],
    )
    type: str = Field(
        ...,
        description="Идентификатор типа ошибки",
        examples=["greater_than"],
    )


class ValidationErrorResponse(BaseModel):
    detail: list[ValidationErrorItem] = Field(
        ...,
        description="Список ошибок валидации",
    )