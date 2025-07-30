import asyncio
from abc import ABC
from types import TracebackType
from typing import Any, Optional, Type

import httpx

from ozon_price_check.constants import ExternalAPIUrls


class FetchError(Exception):
    """Raised when an HTTP request fails."""


class APIClient(ABC):
    """HTTP client for making API requests with automatic retries and error handling."""

    def __init__(
        self,
        client_id: int,
        api_key: str,
        max_concurrent_requests: int = 10,
        timeout: float = 10.0,
    ):
        self._client: Optional[httpx.AsyncClient] = None
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._timeout = timeout
        self._client_id = client_id
        self._api_key = api_key

    async def __aenter__(self) -> "APIClient":
        self._client = httpx.AsyncClient(
            base_url=ExternalAPIUrls.BASE_URL,
            timeout=httpx.Timeout(self._timeout),
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        if self._client:
            await self._client.aclose()

    def get_default_headers(self) -> dict[str, Any]:
        return {
            "Client-Id": str(self._client_id),
            "Api-Key": str(self._api_key),
            "Content-Type": "application/json",
        }

    async def fetch(
        self,
        url: ExternalAPIUrls,
        body: Optional[dict[str, Any]] = None,
        method: str = "POST",
        headers: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Make an HTTP request to the specified URL."""
        if not self._client:
            raise RuntimeError("Client is not initialized. Use 'async with'.")

        merged_headers = {**self.get_default_headers(), **(headers or {})}

        async with self._semaphore:
            try:
                resp = await self._client.request(
                    method=method.upper(),
                    url=url,
                    json=body,
                    headers=merged_headers,
                )

                resp.raise_for_status()
                return resp.json()

            except httpx.HTTPStatusError as e:
                text = e.response.text
                msg = f"Request failed (url={url}, body={body}), status={e.response.status_code}, response={text}"
                raise FetchError(msg)

            except httpx.RequestError as e:
                msg = (
                    f"HTTP client error for request url={url} body={body}. Details: {e}"
                )
                raise FetchError(msg)
