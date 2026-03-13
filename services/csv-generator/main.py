from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Union
import csv
import io


app = FastAPI(title="CSV Generator Service")


class ProductRow(BaseModel):
    id: Union[int, str]
    name: str
    location: Optional[str] = ""
    barcode: Optional[str] = None


class CsvProductsRequest(BaseModel):
    products: List[ProductRow] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/csv/products", response_class=PlainTextResponse)
def generate_products_csv(payload: CsvProductsRequest):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["id", "name", "location", "barcode"])

    for product in payload.products:
        row = product.model_dump()

        fallback_barcode = f"grcy:p:{row['id']}"
        barcode = row.get("barcode") or fallback_barcode

        writer.writerow(
            [
                row["id"],
                row["name"],
                row.get("location") or "",
                barcode,
            ]
        )

    return output.getvalue()
