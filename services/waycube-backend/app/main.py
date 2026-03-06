from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List
import os
import tempfile
import subprocess

from shared.print_core.print_service import print_pdf


app = FastAPI(title="Waycube Label Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------
# Templates listing
# ----------------------------------------

def get_waycube_templates() -> List[str]:

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../")
    )

    TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates", "waycube")

    templates = []

    for root, _, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith(".glabels"):
                full_path = os.path.join(root, file)

                relative_path = os.path.relpath(
                    full_path,
                    os.path.join(PROJECT_ROOT, "templates")
                )

                templates.append(relative_path)

    return templates


@app.get("/api/waycube/templates")
async def list_templates():
    return get_waycube_templates()


# ----------------------------------------
# Request model
# ----------------------------------------

class LabelRequest(BaseModel):
    template: str


# ----------------------------------------
# CSV generator (1 column)
# ----------------------------------------

def generate_date_csv() -> str:

    now = datetime.now()
    formatted_date = now.strftime("%-d %B %Y")

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline=""
    )

    # 1 kolom
    temp_file.write("date\n")
    temp_file.write(f"{formatted_date}\n")
    temp_file.close()

    return temp_file.name


# ----------------------------------------
# Run glabels
# ----------------------------------------

def run_glabels(csv_path: str, template_name: str) -> str:

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../")
    )

    TEMPLATE_PATH = os.path.join(
        PROJECT_ROOT,
        "templates",
        template_name
    )

    output_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    output_pdf_path = output_pdf.name
    output_pdf.close()

    result = subprocess.run(
        [
            "glabels-3-batch",
            "--input", csv_path,
            "--output", output_pdf_path,
            TEMPLATE_PATH
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return output_pdf_path


# ----------------------------------------
# Generate
# ----------------------------------------

@app.post("/api/waycube/generate")
async def generate_label(request: LabelRequest):

    csv_path = generate_date_csv()
    pdf_path = run_glabels(csv_path, request.template)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="waycube.pdf"
    )


# ----------------------------------------
# Print
# ----------------------------------------

@app.post("/api/waycube/print")
async def print_label(request: LabelRequest):

    csv_path = generate_date_csv()
    pdf_path = run_glabels(csv_path, request.template)

    print_pdf(pdf_path)

    return {"status": "sent to printer"}