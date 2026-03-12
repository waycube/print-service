from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import tempfile
import os

from services import SERVICE_MAP


app = FastAPI(title="Backend Orchestrator")

# ----------------------------
# CORS
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Service endpoints (Docker DNS)
# ----------------------------

TEMPLATE_SERVICE = os.getenv(
    "TEMPLATE_SERVICE",
    "http://glabels-templates:8000"
)

LABEL_GENERATOR = os.getenv(
    "LABEL_GENERATOR",
    "http://label-generator:8000"
)

PRINT_SERVICE = os.getenv(
    "PRINT_SERVICE",
    "http://label-generator:8000"
)

REQUEST_TIMEOUT = 10


# ----------------------------
# Request Model
# ----------------------------

class GenerateRequest(BaseModel):
    service: str
    action: str
    template: str
    payload: dict


# ==========================================================
# TEMPLATES
# ==========================================================

@app.get("/templates")
def list_templates():
    try:
        response = requests.get(
            f"{TEMPLATE_SERVICE}/templates",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Template service unavailable"
        )


# ==========================================================
# GROCY ITEMS PROXY
# ==========================================================

@app.get("/grocy/items")
def get_grocy_items():

    if "grocy" not in SERVICE_MAP:
        raise HTTPException(
            status_code=400,
            detail="Grocy service not configured"
        )

    try:
        response = requests.get(
            f"{SERVICE_MAP['grocy']}/items",
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Grocy service unavailable"
        )


# ==========================================================
# GENERATE (Preview PDF)
# ==========================================================

@app.post("/generate")
def generate_label(request: GenerateRequest):

    service_url = SERVICE_MAP.get(request.service)

    if not service_url:
        raise HTTPException(
            status_code=400,
            detail="Unknown service"
        )

    # ----------------------------
    # 1️⃣ Fetch CSV from service
    # ----------------------------

    try:
        csv_response = requests.post(
            f"{service_url}/csv/{request.action}",
            json=request.payload,
            timeout=REQUEST_TIMEOUT
        )
        csv_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="CSV service failed"
        )

    csv_content = csv_response.text

    # ----------------------------
    # 2️⃣ Download template
    # ----------------------------

    try:
        template_response = requests.get(
            f"{TEMPLATE_SERVICE}/templates/{request.template}",
            timeout=REQUEST_TIMEOUT
        )
        template_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=400,
            detail="Template not found"
        )

    # ----------------------------
    # 3️⃣ Forward multipart to label-generator
    # ----------------------------

    files = {
        "template": (
            "template.glabels",
            template_response.content,
            "application/octet-stream"
        ),
        "csv": (
            "data.csv",
            csv_content.encode("utf-8"),
            "text/csv"
        ),
    }

    try:
        generate_response = requests.post(
            f"{LABEL_GENERATOR}/generate",
            files=files,
            timeout=REQUEST_TIMEOUT
        )
        generate_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Label generation failed"
        )

    # ----------------------------
    # 4️⃣ Return PDF
    # ----------------------------

    pdf_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )

    pdf_file.write(generate_response.content)
    pdf_file.close()

    return FileResponse(
        pdf_file.name,
        media_type="application/pdf",
        filename="label.pdf"
    )


# ==========================================================
# PRINT (Direct to printer)
# ==========================================================

@app.post("/print")
def print_label(request: GenerateRequest):

    service_url = SERVICE_MAP.get(request.service)

    if not service_url:
        raise HTTPException(
            status_code=400,
            detail="Unknown service"
        )

    # Fetch CSV
    try:
        csv_response = requests.post(
            f"{service_url}/csv/{request.action}",
            json=request.payload,
            timeout=REQUEST_TIMEOUT
        )
        csv_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="CSV service failed"
        )

    csv_content = csv_response.text

    # Download template
    try:
        template_response = requests.get(
            f"{TEMPLATE_SERVICE}/templates/{request.template}",
            timeout=REQUEST_TIMEOUT
        )
        template_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=400,
            detail="Template not found"
        )

    files = {
        "template": (
            "template.glabels",
            template_response.content,
            "application/octet-stream"
        ),
        "csv": (
            "data.csv",
            csv_content.encode("utf-8"),
            "text/csv"
        ),
    }

    # Forward to label-generator
    try:
        generate_response = requests.post(
            f"{LABEL_GENERATOR}/generate",
            files=files,
            timeout=REQUEST_TIMEOUT
        )
        generate_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Label generation failed"
        )

    # Send PDF to printer
    try:
        print_response = requests.post(
            f"{PRINT_SERVICE}/print",
            files={
                "pdf": (
                    "label.pdf",
                    generate_response.content,
                    "application/pdf"
                )
            },
            timeout=REQUEST_TIMEOUT
        )
        print_response.raise_for_status()

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Printing failed"
        )

    return {"status": "sent to printer"}