from fastapi import FastAPI

app = FastAPI(title="Label App API")

@app.get("/health")
def health():
    return {"status": "ok"}