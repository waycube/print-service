from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import requests
import os
import csv
import io

app = FastAPI(title="Grocy CSV Service")

GROCY_URL = os.getenv("GROCY_URL", "http://grocy.app.lan/api")
GROCY_API_KEY = os.getenv("GROCY_API_KEY", "")


class GrocyRequest(BaseModel):
    product_ids: list[int]

@app.get("/items")
def list_items():
    headers = {
        "accept": "application/json",
        "GROCY-API-KEY": GROCY_API_KEY
    }

    products_response = requests.get(
        f"{GROCY_URL}/objects/products",
        headers=headers
    )

    return products_response.json()


@app.post("/csv/products", response_class=PlainTextResponse)
def generate_grocy_csv(request: GrocyRequest):

    headers = {
        "accept": "application/json",
        "GROCY-API-KEY": GROCY_API_KEY
    }

    # ----------------------------
    # Fetch data from Grocy
    # ----------------------------

    products_response = requests.get(
        f"{GROCY_URL}/objects/products",
        headers=headers
    )

    locations_response = requests.get(
        f"{GROCY_URL}/objects/locations",
        headers=headers
    )

    barcodes_response = requests.get(
        f"{GROCY_URL}/objects/product_barcodes",
        headers=headers
    )

    if (
        products_response.status_code != 200 or
        locations_response.status_code != 200 or
        barcodes_response.status_code != 200
    ):
        return PlainTextResponse("error", status_code=500)

    products = products_response.json()
    locations = locations_response.json()
    barcodes = barcodes_response.json()

    # ----------------------------
    # Build lookup maps
    # ----------------------------

    location_map = {loc["id"]: loc["name"] for loc in locations}
    barcode_map = {b["product_id"]: b["barcode"] for b in barcodes}

    # ----------------------------
    # Filter selected products
    # ----------------------------

    selected = [
        p for p in products
        if p["id"] in request.product_ids
    ]

    # ----------------------------
    # Generate CSV (robust way)
    # ----------------------------

    output = io.StringIO()
    writer = csv.writer(output)

    # Header EXACT order
    writer.writerow(["id", "name", "location", "barcode"])

    for p in selected:

        location_name = location_map.get(p["location_id"], "")
        barcode = barcode_map.get(p["id"])

        if not barcode:
            barcode = f"grcy:p:{p['id']}"

        writer.writerow([
            p["id"],
            p["name"],
            location_name,
            barcode
        ])

    return output.getvalue()