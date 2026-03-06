from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import tempfile
from services import SERVICE_MAP

app = FastAPI(title="Backend Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATE_SERVICE = "http://glabels-templates:8000"
LABEL_GENERATOR = "http://label-generator:8000"


class GenerateRequest(BaseModel):
    service: str
    action: str
    template: str
    payload: dict


@app.get("/templates")
def list_templates():
    response = requests.get(f"{TEMPLATE_SERVICE}/templates")
    return response.json()


@app.post("/generate")
def generate_label(request: GenerateRequest):

    # ----------------------------
    # 1️⃣ Validate service
    # ----------------------------

    if request.service not in SERVICE_MAP:
        return JSONResponse(
            status_code=400,
            content={"error": "Unknown service"}
        )

    service_url = SERVICE_MAP[request.service]

    # ----------------------------
    # 2️⃣ Fetch CSV from service
    # ----------------------------

    csv_response = requests.post(
        f"{service_url}/csv/{request.action}",
        json=request.payload
    )

    if csv_response.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": "CSV service failed"}
        )

    csv_content = csv_response.text

    # ----------------------------
    # 3️⃣ Download template
    # ----------------------------

    template_response = requests.get(
        f"{TEMPLATE_SERVICE}/templates/{request.template}",
        stream=True
    )

    if template_response.status_code != 200:
        return JSONResponse(
            status_code=400,
            content={"error": "Template not found"}
        )

    # ----------------------------
    # 4️⃣ Multipart forward to label-generator
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

    generate_response = requests.post(
        f"{LABEL_GENERATOR}/generate",
        files=files
    )

    if generate_response.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": "Label generation failed"}
        )

    # ----------------------------
    # 5️⃣ Return PDF
    # ----------------------------

    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file.write(generate_response.content)
    pdf_file.close()

    return FileResponse(
        pdf_file.name,
        media_type="application/pdf",
        filename="label.pdf"
    )