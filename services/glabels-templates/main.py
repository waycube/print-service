from fastapi import FastAPI
from fastapi.responses import FileResponse
import os
from typing import List

app = FastAPI(title="Glabels Template Service")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


@app.get("/templates")
def list_templates() -> List[str]:

    templates = []

    for root, _, files in os.walk(TEMPLATE_DIR):
        for file in files:
            if file.endswith(".glabels"):
                full_path = os.path.join(root, file)

                relative_path = os.path.relpath(
                    full_path,
                    TEMPLATE_DIR
                )

                templates.append(relative_path)

    return templates


@app.get("/templates/{template_path:path}")
def get_template(template_path: str):

    file_path = os.path.join(TEMPLATE_DIR, template_path)

    if not os.path.exists(file_path):
        return {"error": "Template not found"}

    return FileResponse(file_path)