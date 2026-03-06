import csv
import tempfile
from typing import List


def generate_csv(items: List) -> str:
    """
    Accepts any objects that have:
        item.name
        item.location
        item.barcode
    """

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline=""
    )

    writer = csv.writer(temp_file)

    # Header moet matchen met je glabel template velden
    writer.writerow(["name", "location", "barcode"])

    for item in items:
        writer.writerow([
            getattr(item, "id", ""),
            getattr(item, "name", ""),
            getattr(item, "location", ""),
            getattr(item, "barcode", ""),
        ])

    temp_file.close()

    return temp_file.name