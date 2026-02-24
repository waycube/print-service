import csv
import tempfile
from typing import List
from app.models import GenericItem


def generate_csv(items: List[GenericItem]) -> str:
    """
    Generate temporary CSV file from GenericItem list.
    Returns path to CSV file.
    """

    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        delete=False,
        suffix=".csv"
    )

    writer = csv.writer(temp_file)

    # CSV header (must match glabel template)
    writer.writerow(["id", "name", "location", "barcode"])

    for item in items:
        writer.writerow([
            item.id,
            item.name,
            item.location or "",
            item.barcode or ""
        ])

    temp_file.close()

    return temp_file.name