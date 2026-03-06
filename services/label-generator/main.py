from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import subprocess

app = FastAPI(title="Label Generator Service")


@app.post("/generate")
async def generate_label(
    template: UploadFile = File(...),
    csv: UploadFile = File(...)
):

    # Save template file
    template_file = tempfile.NamedTemporaryFile(delete=False, suffix=".glabels")
    template_file.write(await template.read())
    template_file.close()

    # Save CSV file
    csv_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    csv_file.write(await csv.read())
    csv_file.close()

    # Output PDF file
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file.close()

    # Run glabels
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
                "error": result.stderr,
                "stdout": result.stdout
            }
        )

    return FileResponse(pdf_file.name, media_type="application/pdf")