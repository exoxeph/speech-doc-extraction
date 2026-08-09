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
            stdout=(
                "LAB REPORT\n"
                "Patient Name: John Doe\n"
                "Glucose    12.5    mg/dL    10.0 - 15.0\n"
                "Reference Range"
            ),
            stderr="",
        )

    adapter = TesseractOCRAdapter(runner=fake_runner)

    result = asyncio.run(adapter.extract_text(PNG_BYTES))

    assert result.provider == "tesseract"
    assert result.lines == [
        "LAB REPORT",
        "Patient Name: John Doe",
        "Glucose    12.5    mg/dL    10.0 - 15.0",
        "Reference Range",
    ]
    assert calls[0][0][0][0] == "tesseract"
    assert calls[0][1]["capture_output"] is True
    assert calls[0][1]["encoding"] == "utf-8"
    assert calls[0][1]["errors"] == "replace"


def test_tesseract_adapter_retries_sparse_output_with_single_block_psm() -> None:
    calls = []

    def fake_runner(*args, **kwargs):
        calls.append((args, kwargs))
        if len(calls) == 1:
            return subprocess.CompletedProcess(args=args[0], returncode=0, stdout="", stderr="")
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="LAB REPORT\nGlucose value=84.2; unit=mg/dL; range=N/A",
            stderr="",
        )

    adapter = TesseractOCRAdapter(runner=fake_runner)

    result = asyncio.run(adapter.extract_text(PNG_BYTES))

    assert result.lines == [
        "LAB REPORT",
        "Glucose value=84.2; unit=mg/dL; range=N/A",
    ]
    assert calls[0][0][0] == ["tesseract", calls[0][0][0][1], "stdout", "-l", "eng"]
    assert calls[1][0][0][-2:] == ["--psm", "6"]


def test_tesseract_adapter_prefers_psm_output_with_result_rows() -> None:
    calls = []

    def fake_runner(*args, **kwargs):
        calls.append((args, kwargs))
        if len(calls) == 1:
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0,
                stdout="LAB REPORT\nPatient Name: Test Patient\nReference Range\nHemoglobin\n10.5\ng/dL",
                stderr="",
            )
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="LAB REPORT\nHemoglobin 10.5 g/dL 12.0 - 16.0 L",
            stderr="",
        )

    adapter = TesseractOCRAdapter(runner=fake_runner)

    result = asyncio.run(adapter.extract_text(PNG_BYTES))

    assert result.lines == [
        "LAB REPORT",
        "Hemoglobin 10.5 g/dL 12.0 - 16.0 L",
    ]
    assert calls[1][0][0][-2:] == ["--psm", "6"]


def test_guess_image_suffix_detects_supported_images() -> None:
    assert _guess_image_suffix(b"\xff\xd8\xff\xe0") == ".jpg"
    assert _guess_image_suffix(PNG_BYTES) == ".png"
