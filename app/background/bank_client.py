import asyncio
import logging
import random
import re
from collections.abc import Awaitable, Callable, Mapping
from types import TracebackType
from typing import Self, TypeVar

import httpx
from pydantic import TypeAdapter

from app.config import NBRBSettings
from app.core.exceptions import (
    NBRBAPIException,
    NBRBClientException,
    NBRBNetworkException,
    NBRBResponseValidationException,
)
from app.schemas.nbrb import NBRBCurrency, NBRBRate


class NBRBClientAdapter:
    def __init__(self, client: NBRBClient) -> None:
        self._client = client

    async def get_rates(self, periodicity: int = 0) -> list[NBRBRate]:
        try:
            return await self._client.get_rates(periodicity)
        except NBRBClientException:
            return []

    async def get_rate(self, cur_code: str) -> NBRBRate:
        try:
            return await self._client.get_rate(cur_code)
        except NBRBClientException as exc:
            raise exc

    async def get_currencies(self) -> list[NBRBCurrency]:
        try:
            return await self._client.get_currencies()
        except NBRBClientException:
            return []

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self._client.__aexit__(exc_type, exc, tb)

    async def aclose(self) -> None:
        await self._client.aclose()

class NBRBClient:
    _RETRY_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})

    _rates_adapter = TypeAdapter(list[NBRBRate])
    _currencies_adapter = TypeAdapter(list[NBRBCurrency])

    def __init__(
        self,
        config: NBRBSettings,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=str(config.api_base_url).rstrip("/") + "/",
            timeout=httpx.Timeout(config.timeout),
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_rates(self, periodicity: int = 0) -> list[NBRBRate]:
        response = await self._request(
            "GET",
            "exrates/rates",
            params={"periodicity": periodicity},
        )
        try:
            return self._rates_adapter.validate_python(response.json())
        except ValueError as exc:
            raise NBRBResponseValidationException(str(exc)) from exc

    async def get_rate(self, cur_code: str) -> NBRBRate:
        response = await self._request(
            "GET",
            f"exrates/rates/{cur_code}",
            params={"parammode": 2},
        )
        try:
            return NBRBRate.model_validate(response.json())
        except ValueError as exc:
            raise NBRBResponseValidationException(str(exc)) from exc

    async def get_currencies(self) -> list[NBRBCurrency]:
        response = await self._request("GET", "exrates/currencies")
        try:
            return self._currencies_adapter.validate_python(response.json())
        except ValueError as exc:
            raise NBRBResponseValidationException(str(exc)) from exc

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, int | str] | None = None,
    ) -> httpx.Response:
        last_error: NBRBClientException | None = None
        max_retry_range = self.config.max_retries + 1
        for attempt in range(max_retry_range):
            try:
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as exc:
                error = NBRBAPIException(
                    status_code=exc.response.status_code,
                    response_body=exc.response.text,
                )
                if (
                    exc.response.status_code not in self._RETRY_STATUS_CODES
                    or attempt >= self.config.max_retries
                ):
                    raise error from exc
                last_error = error
            except httpx.RequestError as exc:
                error = NBRBNetworkException(str(exc))
                if attempt >= self.config.max_retries:
                    raise error from exc
                last_error = error

            await asyncio.sleep(self._retry_delay(attempt))

        raise last_error or NBRBNetworkException(
            "Превышено количество попыток запроса к API НБ РБ.",
        )

    def _retry_delay(self, attempt: int) -> float:
        exponential_delay = self.config.retry_backoff * (2**attempt)
        jitter = random.uniform(0, self.config.retry_jitter * (2**attempt))
        return exponential_delay + jitter



