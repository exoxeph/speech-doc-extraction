from pathlib import Path

from app.adapters.ocr.base import OCRProvider
from app.adapters.ocr.mock import MockOCRAdapter
from app.adapters.ocr.tesseract import TesseractOCRAdapter
from app.config import Settings


def create_ocr_provider(settings: Settings) -> OCRProvider:
    if settings.ocr_provider == "mock":
        return MockOCRAdapter(_resolve_project_path(settings.mock_ocr_response_dir))

    if settings.ocr_provider == "tesseract":
        return TesseractOCRAdapter()

    raise ValueError(f"Unsupported OCR provider: {settings.ocr_provider}")


def _resolve_project_path(path: Path) -> Path:
    if path.is_absolute():
        return path

    project_root = Path(__file__).resolve().parents[3]
    return project_root / path
