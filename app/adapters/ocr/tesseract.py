import subprocess
import tempfile
import re
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
            completed = self._run_tesseract(image_path)
            completed = _better_result(
                completed,
                self._run_tesseract(image_path, ["--psm", "6"]),
            )
            if _ocr_signal_score(completed.stdout) < 8:
                for candidate_path in _create_preprocessed_candidates(image_path):
                    try:
                        completed = _better_result(
                            completed,
                            self._run_tesseract(candidate_path, ["--psm", "6"]),
                        )
                    finally:
                        candidate_path.unlink(missing_ok=True)
        finally:
            image_path.unlink(missing_ok=True)

        return OCRResult(
            lines=completed.stdout.splitlines(),
            provider="tesseract",
        )

    def _run_tesseract(
        self, image_path: Path, extra_args: list[str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        command = [self.command, str(image_path), "stdout", "-l", "eng"]
        if extra_args:
            command.extend(extra_args)

        return self.runner(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )


def _guess_image_suffix(document: bytes) -> str:
    if document.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if document.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"

    return ".image"


def _better_result(
    current: subprocess.CompletedProcess[str],
    candidate: subprocess.CompletedProcess[str],
) -> subprocess.CompletedProcess[str]:
    if _ocr_signal_score(candidate.stdout) > _ocr_signal_score(current.stdout):
        return candidate

    return current


def _ocr_signal_score(text: str | None) -> int:
    if not text:
        return 0

    meaningful_lines = [line for line in text.splitlines() if line.strip()]
    lowered = text.lower()
    keyword_score = sum(
        lowered.count(keyword)
        for keyword in [
            "lab",
            "report",
            "patient",
            "facility",
            "glucose",
            "creatinine",
            "sodium",
            "value",
            "unit",
            "range",
        ]
    )
    row_score = sum(1 for line in meaningful_lines if _looks_like_result_row(line))
    return min(len(meaningful_lines), 3) + keyword_score + (row_score * 5)


def _looks_like_result_row(line: str) -> bool:
    return bool(
        re.search(r"\d", line)
        and re.search(
            r"\b(?:mg/dl|g/dl|gm/dl|mmol/l|10\*?3/|10\^3/|m[l1]/min)\b",
            line,
            flags=re.IGNORECASE,
        )
    )


def _create_preprocessed_candidates(image_path: Path) -> list[Path]:
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return []

    image = Image.open(image_path).convert("RGB")
    candidates: list[Path] = []
    for angle in [-10, 10]:
        rotated = image.rotate(angle, expand=True, fillcolor=(30, 30, 30))
        processed = ImageOps.autocontrast(ImageOps.grayscale(rotated))
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as candidate_file:
            candidate_path = Path(candidate_file.name)
        processed.save(candidate_path)
        candidates.append(candidate_path)

    return candidates
