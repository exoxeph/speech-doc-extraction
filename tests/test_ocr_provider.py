import asyncio

from app.adapters.ocr.base import OCRProvider, OCRResult


class FakeOCRProvider:
    async def extract_text(self, document: bytes) -> OCRResult:
        return OCRResult(
            lines=[
                "Patient Name: John Doe",
                "Hemoglobin    12.5    gm/dl    13.0 - 17.0",
            ],
            provider="fake",
        )


def test_ocr_provider_contract_preserves_lines_for_calling_code() -> None:
    provider: OCRProvider = FakeOCRProvider()

    result = asyncio.run(provider.extract_text(b"image bytes"))

    assert result.provider == "fake"
    assert result.lines == [
        "Patient Name: John Doe",
        "Hemoglobin    12.5    gm/dl    13.0 - 17.0",
    ]
