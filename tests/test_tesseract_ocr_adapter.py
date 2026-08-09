import asyncio
import subprocess

from app.adapters.ocr.tesseract import TesseractOCRAdapter, _guess_image_suffix


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"mock png bytes"


def test_tesseract_adapter_maps_stdout_to_ocr_lines() -> None:
    calls = []

    def fake_runner(*args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="Patient Name: John Doe\nHemoglobin    12.5    gm/dl",
            stderr="",
        )

    adapter = TesseractOCRAdapter(runner=fake_runner)

    result = asyncio.run(adapter.extract_text(PNG_BYTES))

    assert result.provider == "tesseract"
    assert result.lines == [
        "Patient Name: John Doe",
        "Hemoglobin    12.5    gm/dl",
    ]
    assert calls[0][0][0][0] == "tesseract"
    assert calls[0][1]["capture_output"] is True
    assert calls[0][1]["encoding"] == "utf-8"
    assert calls[0][1]["errors"] == "replace"


def test_guess_image_suffix_detects_supported_images() -> None:
    assert _guess_image_suffix(b"\xff\xd8\xff\xe0") == ".jpg"
    assert _guess_image_suffix(PNG_BYTES) == ".png"
