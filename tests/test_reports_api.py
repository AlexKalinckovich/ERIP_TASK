# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.error_response import ErrorResponse  # noqa: F401
from openapi_server.models.summary_report_response import SummaryReportResponse  # noqa: F401
from openapi_server.models import ValidationErrorResponse  # noqa: F401


def test_get_deals_summary_report(client: TestClient):
    """Test case for get_deals_summary_report

    Получение агрегированного отчёта по сделкам за интервал времени
    """
    params = [("date_from", '2026-10-01T00:00:00Z'),     ("date_to", '2026-10-26T23:59:59Z'),     ("currency", 'USD')]
    headers = {
        "x_request_id": 'x_request_id_example',
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/v1/deals/reports/summary",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

