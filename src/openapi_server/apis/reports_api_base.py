# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.error_response import ErrorResponse
from openapi_server.models.summary_report_response import SummaryReportResponse
from openapi_server.models.validation_error_response import ValidationErrorResponse


class BaseReportsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseReportsApi.subclasses = BaseReportsApi.subclasses + (cls,)
    def get_deals_summary_report(
        self,
        date_from: str,
        date_to: str,
        currency: str,
        x_request_id: str,
    ) -> SummaryReportResponse:
        """Возвращает сводную статистику движения денежных средств в кассе (сумма полученного,  сумма ушедшего, количество сделок) по каждой валюте за указанный интервал времени. """
        ...
