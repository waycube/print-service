from pydantic import BaseModel
from typing import Optional, Dict


class GenericItem(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    barcode: Optional[str] = None
    extra: Dict = {}