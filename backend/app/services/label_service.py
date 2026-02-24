import subprocess
import tempfile
from typing import List

from app.models import GenericItem
from app.services.csv_exporter import generate_csv


def create_label_pdf(items: List[GenericItem]) -> str:
    """
    Generates CSV from items and calls glabels-3-batch
    Returns path to generated PDF
    """

    # 1️⃣ Generate CSV
    csv_path = generate_csv(items)

    # 2️⃣ Prepare output PDF file
    output_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    output_pdf_path = output_pdf.name
    output_pdf.close()

    # 3️⃣ Path to your template
    # ⚠️ IMPORTANT: adjust this to your real template location
    template_path = "57mmx32mm_template.glabels"

    # 4️⃣ Call glabels
    try:
        subprocess.run(
            [
                "glabels-3-batch",
                "--template", template_path,
                "--data", csv_path,
                "--output", output_pdf_path
            ],
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"gLabels failed: {e}")

    return output_pdf_path