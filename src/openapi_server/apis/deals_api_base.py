# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.create_deal_request import CreateDealRequest
from openapi_server.models.deal_quote_response import DealQuoteResponse
from openapi_server.models.deal_status_response import DealStatusResponse
from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.pending_deals_response import PendingDealsResponse
from openapi_server.models.update_deal_request import UpdateDealRequest
from openapi_server.models.validation_error_response import ValidationErrorResponse


class BaseDealsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseDealsApi.subclasses = BaseDealsApi.subclasses + (cls,)
    def create_deal_quote(
        self,
        create_deal_request: CreateDealRequest,
        idempotency_key: str,
        x_request_id: str,
    ) -> DealQuoteResponse:
        """Рассчитывает параметры обмена на основе текущих курсов НБ РБ. """
        ...


    def get_pending_deals(
        self,
        limit: int,
        offset: int,
        x_request_id: str,
    ) -> PendingDealsResponse:
        """Возвращает список всех активных сделок, находящихся в статусе PENDING. """
        ...


    def update_deal_status(
        self,
        deal_id: str,
        update_deal_request: UpdateDealRequest,
        idempotency_key: str,
    ) -> DealStatusResponse:
        """Переводит ранее созданную возможную сделку из статуса PENDING в итоговый статус CONFIRMED или REJECTED. """
        ...
