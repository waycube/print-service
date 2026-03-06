from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import tempfile
import os
from datetime import datetime

app = FastAPI(title="Backend Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tijdelijk voor dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# service URLs (docker service names!)
TEMPLATE_SERVICE = "http://glabels-templates:8000"
LABEL_GENERATOR = "http://label-generator:8000"


class GenerateRequest(BaseModel):
    template: str


@app.get("/templates")
def list_templates():
    response = requests.get(f"{TEMPLATE_SERVICE}/templates")
    return response.json()


@app.post("/generate")
def generate_label(request: GenerateRequest):

    # 1️⃣ Download template
    template_response = requests.get(
        f"{TEMPLATE_SERVICE}/templates/{request.template}"
    )

    if template_response.status_code != 200:
        return {"error": "Template not found"}

    template_file = tempfile.NamedTemporaryFile(delete=False, suffix=".glabels")
    template_file.write(template_response.content)
    template_file.close()

    # 2️⃣ Generate CSV (tijdelijk hardcoded)
    formatted_date = datetime.now().strftime("%-d %B %Y")

    csv_data = f"date\n{formatted_date}\n"

    # 3️⃣ Call label-generator
    generate_response = requests.post(
        f"{LABEL_GENERATOR}/generate",
        json={
            "template_path": template_file.name,
            "csv_data": csv_data
        }
    )

    if generate_response.status_code != 200:
        return {"error": "PDF generation failed"}

    # 4️⃣ Return PDF to frontend
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file.write(generate_response.content)
    pdf_file.close()

    return FileResponse(pdf_file.name, media_type="application/pdf")