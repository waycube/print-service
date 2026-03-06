from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from datetime import datetime

app = FastAPI(title="Office CSV Service")


@app.post("/csv/paid", response_class=PlainTextResponse)
def generate_paid_csv():

    formatted_date = datetime.now().strftime("%-d %B %Y")

    csv_content = f"date\n{formatted_date}\n"

    return csv_content