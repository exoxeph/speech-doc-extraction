from app.services.models import TranscriptionResult


def test_transcription_result_holds_provider_output() -> None:
    result = TranscriptionResult(
        transcript="Hello",
        detected_language="en",
        duration=1.5,
        provider="mock",
    )

    assert result.transcript == "Hello"
    assert result.detected_language == "en"
    assert result.duration == 1.5
    assert result.provider == "mock"
