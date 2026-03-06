import subprocess
import tempfile
import os
from typing import List

from shared.label_core.csv_exporter import generate_csv


def create_label_pdf(items: List, template_name: str) -> str:
    """
    Generates a PDF using glabels.
    template_name should include subfolder, e.g.:
        "grocy/57x32-grocy.glabels"
        "waycube/paid_label.glabels"
    """

    # Generate CSV
    csv_path = generate_csv(items)

    # Create temp output PDF
    output_pdf = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    )
    output_pdf_path = output_pdf.name
    output_pdf.close()

    # Determine project root (label-system/)
    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../")
    )

    # Templates directory
    TEMPLATE_DIR = os.path.join(PROJECT_ROOT, "templates")

    # Full template path (includes subfolder)
    template_path = os.path.join(TEMPLATE_DIR, template_name)

    if not os.path.exists(template_path):
        raise RuntimeError(f"Template not found: {template_path}")

    # Run glabels
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