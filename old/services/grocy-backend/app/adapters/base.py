from abc import ABC, abstractmethod
from typing import List
from app.models import GenericItem


class BaseAdapter(ABC):

    @abstractmethod
    async def list_items(self) -> List[GenericItem]:
        pass

    @abstractmethod
    async def get_item(self, item_id: str) -> GenericItem:
        pass

    @abstractmethod
    async def search(self, query: str) -> List[GenericItem]:
        pass