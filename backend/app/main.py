from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List

from app.models import GenericItem
from app.adapters.grocy import GrocyAdapter


from app.services.label_service import create_label_pdf
from app.services.template_service import get_templates

app = FastAPI(title="Label App API")

# --- CORS configuratie ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Adapter instantie ---
adapter = GrocyAdapter()


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


# --- Label generation endpoint ---
from pydantic import BaseModel


class LabelRequest(BaseModel):
    item_ids: List[str]
    template: str


@app.post("/api/labels/generate")
async def generate_labels(request: LabelRequest):

    items = []

    for item_id in request.item_ids:
        item = await adapter.get_item(item_id)
        items.append(item)

    pdf_path = create_label_pdf(items, request.template)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="labels.pdf"
    )

@app.get("/api/templates")
async def list_templates():
    return get_templates()