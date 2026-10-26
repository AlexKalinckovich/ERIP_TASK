# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models import CreateDealRequest  # noqa: F401
from openapi_server.models.deal_quote_response import DealQuoteResponse  # noqa: F401
from openapi_server.models.deal_status_response import DealStatusResponse  # noqa: F401
from openapi_server.models.error_response import ErrorResponse  # noqa: F401
from openapi_server.models import PendingDealsResponse  # noqa: F401
from openapi_server.models import UpdateDealRequest  # noqa: F401
from openapi_server.models import ValidationErrorResponse  # noqa: F401


def test_create_deal_quote(client: TestClient):
    """Test case for create_deal_quote

    Создание предварительной сделки на обмен валют
    """
    create_deal_request = {"source_currency":"USD","amount":100.0,"target_currency":"BYN"}

    headers = {
        "idempotency_key": 'idempotency_key_example',
        "x_request_id": 'x_request_id_example',
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/api/v1/deals",
    #    headers=headers,
    #    json=create_deal_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_get_pending_deals(client: TestClient):
    """Test case for get_pending_deals

    Получение списка незавершённых сделок
    """
    params = [("limit", 20),     ("offset", 0)]
    headers = {
        "x_request_id": 'x_request_id_example',
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/api/v1/deals/pending",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_update_deal_status(client: TestClient):
    """Test case for update_deal_status

    Подтверждение или отклонение обмена валют
    """
    update_deal_request = {"action":"CONFIRM"}

    headers = {
        "idempotency_key": 'idempotency_key_example',
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/api/v1/deals/{deal_id}".format(deal_id='deal_id_example'),
    #    headers=headers,
    #    json=update_deal_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

