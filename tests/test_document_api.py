from fastapi.testclient import TestClient
import pytest

from app.main import app


JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"mock jpeg bytes"
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"mock png bytes"


def test_document_extraction_endpoint_returns_mock_lab_report_result() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.jpg", JPEG_BYTES, "image/jpeg")},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["document_type"] == "lab_report"
    assert body["provider"] == "mock"
    assert body["meta"]["patient_name"] == "John Doe"
    assert body["results"][0]["test_name"] == "Hemoglobin"
    assert body["results"][0]["value"]["numeric"] == 12.5
    assert body["results"][0]["unit"] == "g/dL"
    assert body["results"][0]["raw_line"] == "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"


@pytest.mark.parametrize(
    ("filename", "content", "content_type"),
    [
        ("report.jpg", JPEG_BYTES, "image/jpeg"),
        ("report.jpeg", JPEG_BYTES, "image/jpeg"),
        ("report.png", PNG_BYTES, "image/png"),
    ],
)
def test_document_extraction_endpoint_accepts_supported_image_formats(
    filename: str,
    content: bytes,
    content_type: str,
) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": (filename, content, content_type)},
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "mock"


def test_document_extraction_endpoint_rejects_unsupported_document_format() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.txt", b"text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "UNSUPPORTED_DOCUMENT_FORMAT",
            "message": "Supported document formats are jpg, jpeg and png.",
        }
    }


def test_document_extraction_endpoint_rejects_malformed_image() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.jpg", b"not really an image", "image/jpeg")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "MALFORMED_DOCUMENT",
            "message": "Uploaded document is not a valid jpg, jpeg or png image.",
        }
    }
