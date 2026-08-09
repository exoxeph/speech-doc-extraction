from fastapi.testclient import TestClient

from app.main import app


def test_document_extraction_endpoint_returns_mock_lab_report_result() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/documents/extract",
        files={"file": ("report.jpg", b"normal_report", "image/jpeg")},
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
