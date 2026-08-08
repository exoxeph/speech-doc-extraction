import importlib
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from app.services.models import TranscriptionResult


class FasterWhisperTranscriptionAdapter:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        model_factory: Callable[..., Any] | None = None,
    ) -> None:
        if model_factory is None:
            faster_whisper = importlib.import_module("faster_whisper")
            model_factory = faster_whisper.WhisperModel

        self.model = model_factory(
            model_size,
            device=device,
            compute_type=compute_type,
        )

    async def transcribe(self, audio: bytes, language: str) -> TranscriptionResult:
        if not audio or audio.strip(b"\x00") == b"":
            return TranscriptionResult(
                transcript="",
                detected_language=None,
                duration=0.0,
                provider="faster-whisper",
            )

        suffix = _guess_audio_suffix(audio)
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as audio_file:
            audio_file.write(audio)
            audio_path = Path(audio_file.name)

        try:
            language_arg = None if language == "auto" else language
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language_arg,
                vad_filter=True,
            )
            segment_list = list(segments)
        finally:
            audio_path.unlink(missing_ok=True)

        transcript = " ".join(
            segment.text.strip()
            for segment in segment_list
            if segment.text and segment.text.strip()
        ).strip()

        if transcript == "":
            detected_language = None
        else:
            detected_language = getattr(info, "language", language_arg)

        return TranscriptionResult(
            transcript=transcript,
            detected_language=detected_language,
            duration=float(getattr(info, "duration", 0.0)),
            provider="faster-whisper",
        )


def _guess_audio_suffix(audio: bytes) -> str:
    if audio.startswith(b"RIFF") and b"WAVE" in audio[:16]:
        return ".wav"
    if audio.startswith(b"ID3") or audio[:2] in {b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"}:
        return ".mp3"
    if b"ftyp" in audio[:16]:
        return ".m4a"

    return ".audio"
