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

            # Products
            products = (
                await client.get(
                    f"{self.base_url}/api/objects/products",
                    headers=self.headers
                )
            ).json()

            # Locations
            locations = (
                await client.get(
                    f"{self.base_url}/api/objects/locations",
                    headers=self.headers
                )
            ).json()

            # Product barcodes
            product_barcodes = (
                await client.get(
                    f"{self.base_url}/api/objects/product_barcodes",
                    headers=self.headers
                )
            ).json()

        # Map location_id → name
        location_map = {
            location["id"]: location["name"]
            for location in locations
        }

        # Map product_id → first barcode
        barcode_map = {}

        for entry in product_barcodes:
            product_id = entry.get("product_id")
            barcode = entry.get("barcode")

            if product_id and barcode:
                # Only first barcode per product
                if product_id not in barcode_map:
                    barcode_map[product_id] = barcode

        items = []

        for product in products:

            product_id = product["id"]

            location_name = None
            location_id = product.get("location_id")
            if location_id:
                location_name = location_map.get(location_id)

            # Real barcode if available
            barcode = barcode_map.get(product_id)

            # Fallback to Grocy product code
            if not barcode:
                barcode = f"grcy:p:{product_id}"

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