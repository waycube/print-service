import httpx
from typing import List

from app.adapters.base import BaseAdapter
from app.models import GenericItem
from app.config import GROCY_BASE_URL, GROCY_API_KEY


class GrocyAdapter(BaseAdapter):

    def __init__(self):
        self.base_url = GROCY_BASE_URL.rstrip("/")
        self.headers = {
            "GROCY-API-KEY": GROCY_API_KEY,
            "Accept": "application/json"
        }

    async def list_items(self) -> List[GenericItem]:

        async with httpx.AsyncClient() as client:
            products_response = await client.get(
                f"{self.base_url}/api/objects/products",
                headers=self.headers
            )
            products_response.raise_for_status()
            products = products_response.json()

            stock_response = await client.get(
                f"{self.base_url}/api/stock",
                headers=self.headers
            )
            stock_response.raise_for_status()
            stock_items = stock_response.json()

        # Map stock by product_id
        stock_map = {}
        for stock in stock_items:
            stock_map[stock["product_id"]] = stock

        items = []

        for product in products:
            product_id = product["id"]

            stock_info = stock_map.get(product_id)

            location_name = None
            if stock_info and stock_info.get("location"):
                location_name = stock_info["location"]["name"]

            barcode = product.get("barcode")

            items.append(
                GenericItem(
                    id=str(product_id),
                    name=product["name"],
                    location=location_name,
                    barcode=barcode,
                    extra={}
                )
            )

        return items

    async def get_item(self, item_id: str) -> GenericItem:
        items = await self.list_items()
        for item in items:
            if item.id == item_id:
                return item
        raise ValueError("Item not found")

    async def search(self, query: str) -> List[GenericItem]:
        items = await self.list_items()
        return [
            item for item in items
            if query.lower() in item.name.lower()
        ]