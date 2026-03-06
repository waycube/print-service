from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import tempfile
import subprocess
import requests
import os

app = FastAPI(title="Label Generator Service")

# Interne Docker service naam
TEMPLATE_SERVICE = "http://glabels-templates:8000"


class GenerateRequest(BaseModel):
    template: str
    csv_data: str


@app.post("/generate")
async def generate_label(request: GenerateRequest):

    # ----------------------------
    # 1️⃣ Download template (binary safe)
    # ----------------------------

    template_url = f"{TEMPLATE_SERVICE}/templates/{request.template}"

    template_response = requests.get(template_url, stream=True)

    if template_response.status_code != 200:
        return JSONResponse(
            status_code=400,
            content={"error": f"Template not found: {request.template}"}
        )

    template_file = tempfile.NamedTemporaryFile(delete=False, suffix=".glabels")

    for chunk in template_response.iter_content(chunk_size=8192):
        template_file.write(chunk)

    template_file.close()

    # ----------------------------
    # 2️⃣ Write CSV to temp file
    # ----------------------------

    csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    csv_file.write(request.csv_data.encode("utf-8"))
    csv_file.close()

    # ----------------------------
    # 3️⃣ Prepare output PDF file
    # ----------------------------

    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file.close()

    # ----------------------------
    # 4️⃣ Run glabels-3-batch
    # ----------------------------

    result = subprocess.run(
        [
            "glabels-3-batch",
            "--input", csv_file.name,
            "--output", pdf_file.name,
            template_file.name
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return JSONResponse(
            status_code=500,
            content={
                "error": "glabels failed",
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        )

    return FileResponse(
        pdf_file.name,
        media_type="application/pdf",
        filename="label.pdf"
    )