import subprocess
import tempfile
from collections.abc import Callable
from pathlib import Path

from app.adapters.ocr.base import OCRResult


class TesseractOCRAdapter:
    def __init__(
        self,
        command: str = "tesseract",
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self.command = command
        self.runner = runner

    async def extract_text(self, document: bytes) -> OCRResult:
        suffix = _guess_image_suffix(document)
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as image_file:
            image_file.write(document)
            image_path = Path(image_file.name)

        try:
            completed = self.runner(
                [self.command, str(image_path), "stdout", "-l", "eng"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        finally:
            image_path.unlink(missing_ok=True)

        return OCRResult(
            lines=completed.stdout.splitlines(),
            provider="tesseract",
        )


def _guess_image_suffix(document: bytes) -> str:
    if document.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if document.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    return ".image"
