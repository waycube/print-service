from typing import List
from app.adapters.base import BaseAdapter
from app.models import GenericItem


class MockAdapter(BaseAdapter):

    async def list_items(self) -> List[GenericItem]:
        return [
            GenericItem(
                id="1",
                name="Milk",
                location="Fridge",
                barcode="123456789",
                extra={"stock": 2}
            ),
            GenericItem(
                id="2",
                name="Rice",
                location="Pantry",
                barcode="987654321",
                extra={"stock": 5}
            )
        ]

    async def get_item(self, item_id: str) -> GenericItem:
        items = await self.list_items()
        for item in items:
            if item.id == item_id:
                return item
        raise ValueError("Item not found")

    async def search(self, query: str) -> List[GenericItem]:
        items = await self.list_items()
        return [item for item in items if query.lower() in item.name.lower()]