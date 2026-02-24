from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from app.models import GenericItem
from app.adapters.mock import MockAdapter

app = FastAPI(title="Label App API")

# --- CORS configuratie ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Adapter instantie ---
adapter = MockAdapter()


# --- Health check ---
@app.get("/health")
def health():
    return {"status": "ok"}


# --- Items endpoints ---
@app.get("/api/items", response_model=List[GenericItem])
async def list_items():
    return await adapter.list_items()


@app.get("/api/items/search", response_model=List[GenericItem])
async def search_items(q: str):
    return await adapter.search(q)


@app.get("/api/items/{item_id}", response_model=GenericItem)
async def get_item(item_id: str):
    try:
        return await adapter.get_item(item_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Item not found")