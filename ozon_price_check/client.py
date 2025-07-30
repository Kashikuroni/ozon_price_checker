from ozon_price_check.core_client import APIClient
from ozon_price_check.constants import ExternalAPIUrls
from ozon_price_check.schemas import Item, ProductsResponse


class ProductsAPIClient:
    """Client for fetching product information from OZON API."""

    def __init__(self, client: APIClient):
        self.client = client

    async def get_product_info(self, sku: str) -> Item:
        """Fetch product information by SKU."""
        request_body = {
            "filter": {
                "offer_id": [sku],
                "visibility": "ALL",
            },
            "limit": 1,
        }

        products_data = await self.client.fetch(
            url=ExternalAPIUrls.PRODUCT_PRICE_LIST,
            body=request_body,
        )

        if not products_data:
            raise ValueError(f"Empty response from API for SKU: {sku}")

        price_response = ProductsResponse.model_validate(products_data)

        if not price_response.items:
            raise ValueError(f"No prices found for SKU: {sku}")

        return price_response.items[0]
