from fastapi.testclient import TestClient
import pytest

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


@pytest.mark.parametrize("language", ["bn", "en", "auto"])
def test_transcription_endpoint_accepts_supported_languages(language: str) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio", "audio/wav")},
        data={"language": language},
    )

    assert response.status_code == 200
    assert response.json()["provider"] == "mock"


@pytest.mark.parametrize("language", ["fr", "english", "xyz", ""])
def test_transcription_endpoint_rejects_invalid_languages(language: str) -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/transcribe",
        files={"file": ("sample.wav", b"fake audio", "audio/wav")},
        data={"language": language},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "INVALID_LANGUAGE",
            "message": "Supported languages are bn, en and auto.",
        }
    }
