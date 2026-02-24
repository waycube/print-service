import subprocess
import tempfile
import os
from typing import List

from app.models import GenericItem
from app.services.csv_exporter import generate_csv


def create_label_pdf(items: List[GenericItem], template_name: str) -> str:

    csv_path = generate_csv(items)

    output_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    output_pdf_path = output_pdf.name
    output_pdf.close()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(BASE_DIR, template_name)

    if not os.path.exists(template_path):
        raise RuntimeError(f"Template not found: {template_path}")

    result = subprocess.run(
        [
            "glabels-3-batch",
            "--input", csv_path,
            "--output", output_pdf_path,
            template_path
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"Return code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return output_pdf_path