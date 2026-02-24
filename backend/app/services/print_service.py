import cups
import os


PRINTER_NAME = "Zebra_Technologies_ZD421"


def print_pdf(pdf_path: str) -> None:
    """
    Sends PDF to CUPS printer.
    """

    if not os.path.exists(pdf_path):
        raise RuntimeError("PDF file does not exist")

    conn = cups.Connection()

    printers = conn.getPrinters()

    if PRINTER_NAME not in printers:
        raise RuntimeError(f"Printer {PRINTER_NAME} not found")

    conn.printFile(
        PRINTER_NAME,
        pdf_path,
        "Grocy Labels",
        {}
    )