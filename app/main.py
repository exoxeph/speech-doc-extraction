from fastapi import FastAPI


app = FastAPI(title="Speech and Document Extraction API")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
