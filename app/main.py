from fastapi import FastAPI

from app.api.routes.transcription import router as transcription_router


app = FastAPI(title="Speech and Document Extraction API")
app.include_router(transcription_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
