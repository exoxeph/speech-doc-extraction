import asyncio
from types import SimpleNamespace

from app.adapters.transcription.faster_whisper import (
    FasterWhisperTranscriptionAdapter,
    _guess_audio_suffix,
)


class FakeWhisperModel:
    def __init__(self, model_size: str, device: str, compute_type: str) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: str, language: str | None, vad_filter: bool):
        segments = [
            SimpleNamespace(text=" Hello "),
            SimpleNamespace(text=" world. "),
        ]
        info = SimpleNamespace(language=language or "en", duration=2.5)
        return segments, info


def test_faster_whisper_adapter_maps_segments_to_result() -> None:
    adapter = FasterWhisperTranscriptionAdapter(model_factory=FakeWhisperModel)

    result = asyncio.run(adapter.transcribe(b"fake audio", "auto"))

    assert result.transcript == "Hello world."
    assert result.detected_language == "en"
    assert result.duration == 2.5
    assert result.provider == "faster-whisper"


def test_faster_whisper_adapter_returns_empty_result_for_silence() -> None:
    adapter = FasterWhisperTranscriptionAdapter(model_factory=FakeWhisperModel)

    result = asyncio.run(adapter.transcribe(b"\x00" * 100, "en"))

    assert result.transcript == ""
    assert result.detected_language is None
    assert result.duration == 0.0
    assert result.provider == "faster-whisper"


def test_guess_audio_suffix_detects_aac_adts_header() -> None:
    assert _guess_audio_suffix(bytes.fromhex("FF F9 4C 80")) == ".aac"
