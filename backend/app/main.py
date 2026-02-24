from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from pydantic import BaseModel

from app.models import GenericItem
from app.adapters.grocy import GrocyAdapter
from app.services.label_service import create_label_pdf
from app.services.template_service import get_templates
from app.services.print_service import print_pdf

app = FastAPI(title="Label App API")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Adapter ---
adapter = GrocyAdapter()


# ----------------------------
# Health
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# ----------------------------
# Items
# ----------------------------
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


# ----------------------------
# Templates
# ----------------------------
@app.get("/api/templates")
async def list_templates():
    return get_templates()


# ----------------------------
# Request Models
# ----------------------------
class LabelRequest(BaseModel):
    item_ids: List[str]
    template: str


# ----------------------------
# Generate PDF (preview)
# ----------------------------
@app.post("/api/labels/generate")
async def generate_labels(request: LabelRequest):

    items = []

    for item_id in request.item_ids:
        try:
            item = await adapter.get_item(item_id)
            items.append(item)
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found"
            )

    pdf_path = create_label_pdf(items, request.template)

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="labels.pdf"
    )


# ----------------------------
# Direct Print via CUPS
# ----------------------------
@app.post("/api/labels/print")
async def print_labels(request: LabelRequest):

    items = []

    for item_id in request.item_ids:
        try:
            item = await adapter.get_item(item_id)
            items.append(item)
        except ValueError:
            raise HTTPException(
                status_code=404,
                detail=f"Item {item_id} not found"
            )

    pdf_path = create_label_pdf(items, request.template)

    try:
        print_pdf(pdf_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Print failed: {str(e)}"
        )

    return {"status": "sent to printer"}