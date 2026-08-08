from fastapi.testclient import TestClient

from app.main import app


def test_transcription_endpoint_returns_mock_result() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio", "audio/wav")},
        data={"language": "en"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["transcript"] == "Hello, this is a test."
    assert body["detected_language"] == "en"
    assert body["duration"] == 2.4
    assert body["provider"] == "mock"
