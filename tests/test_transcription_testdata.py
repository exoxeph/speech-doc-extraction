import json
from pathlib import Path


def test_transcription_reference_files_exist() -> None:
    audio_dir = Path("testdata/audio")
    references = json.loads(
        (audio_dir / "reference_transcripts.json").read_text(encoding="utf-8")
    )

    audio_entries = {
        filename: metadata
        for filename, metadata in references.items()
        if not filename.startswith("_")
    }

    assert audio_entries
    for filename in audio_entries:
        path = audio_dir / filename
        assert path.exists(), f"Missing audio fixture: {filename}"
        assert path.stat().st_size > 44
