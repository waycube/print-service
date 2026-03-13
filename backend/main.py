from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional, Union
import os
import requests


app = FastAPI(title="Backend Service")

GROCY_SERVICE_URL = os.getenv("GROCY_SERVICE_URL", "http://grocy:8000")
CSV_GENERATOR_URL = os.getenv("CSV_GENERATOR_URL", "http://csv-generator:8000")
TEMPLATE_SERVICE_URL = os.getenv("TEMPLATE_SERVICE_URL", "http://glabels-templates:8000")
LABEL_GENERATOR_URL = os.getenv("LABEL_GENERATOR_URL", "http://label-generator:8000")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))


class ProductRow(BaseModel):
    id: Union[int, str]
    name: str
    location: Optional[str] = ""
    barcode: Optional[str] = None


class CsvProductsRequest(BaseModel):
    products: List[ProductRow] = Field(default_factory=list)


class GenerateLabelRequest(BaseModel):
    products: List[ProductRow] = Field(default_factory=list)
    template_path: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products/grocy")
def get_grocy_products():
    try:
        response = requests.get(
            f"{GROCY_SERVICE_URL}/items",
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Grocy service error: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Grocy service returned status {response.status_code}",
        )

    return response.json()


@app.post("/csv/products")
def generate_csv(payload: CsvProductsRequest):
    try:
        response = requests.post(
            f"{CSV_GENERATOR_URL}/csv/products",
            json=payload.model_dump(),
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"CSV generator error: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"CSV generator returned status {response.status_code}",
        )

    return Response(content=response.text, media_type="text/csv")


@app.get("/templates")
def list_templates():
    try:
        response = requests.get(
            f"{TEMPLATE_SERVICE_URL}/templates",
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Template service error: {exc}") from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Template service returned status {response.status_code}",
        )

    return response.json()


@app.post("/labels/generate")
def generate_label(payload: GenerateLabelRequest):
    # 1) Build CSV from selected products
    try:
        csv_response = requests.post(
            f"{CSV_GENERATOR_URL}/csv/products",
            json={"products": [p.model_dump() for p in payload.products]},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"CSV generator error: {exc}") from exc

    if csv_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"CSV generator returned status {csv_response.status_code}",
        )

    # 2) Fetch selected template
    try:
        template_response = requests.get(
            f"{TEMPLATE_SERVICE_URL}/templates/{payload.template_path}",
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Template service error: {exc}") from exc

    if template_response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Template service returned status {template_response.status_code}",
        )

    template_filename = os.path.basename(payload.template_path) or "template.glabels"

    # 3) Send template + csv to label generator
    files = {
        "template": (
            template_filename,
            template_response.content,
            "application/xml",
        ),
        "csv": (
            "labels.csv",
            csv_response.text.encode("utf-8"),
            "text/csv",
        ),
    }

    try:
        label_response = requests.post(
            f"{LABEL_GENERATOR_URL}/generate",
            files=files,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Label generator error: {exc}") from exc

    if label_response.status_code != 200:
        detail = label_response.text.strip() or "Label generation failed"
        raise HTTPException(status_code=502, detail=detail)

    return Response(
        content=label_response.content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="labels.pdf"'},
    )
