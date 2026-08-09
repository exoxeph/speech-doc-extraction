import json
from pathlib import Path

from app.adapters.ocr.base import OCRResult


class MockOCRAdapter:
    def __init__(self, response_dir: Path | str) -> None:
        self.response_dir = Path(response_dir)

    async def extract_text(self, document: bytes) -> OCRResult:
        fixture_name = _fixture_name_from_document(document)
        response_path = self.response_dir / f"{fixture_name}.json"

        with response_path.open(encoding="utf-8") as response_file:
            payload = json.load(response_file)

        return OCRResult(
            lines=payload["lines"],
            provider=payload["provider"],
        )


def _fixture_name_from_document(document: bytes) -> str:
    marker = document.decode("utf-8", errors="ignore").strip()
    if marker in {"normal_report", "difficult_report", "not_lab_report"}:
        return marker

    return "normal_report"
