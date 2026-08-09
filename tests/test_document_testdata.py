import json
from pathlib import Path


def test_report_reference_images_exist_and_are_jpegs() -> None:
    report_dir = Path("testdata/reports")
    references = json.loads(
        (report_dir / "reference_reports.json").read_text(encoding="utf-8")
    )

    assert references
    for filename in references:
        image_path = report_dir / filename
        assert image_path.exists(), f"Missing report fixture: {filename}"
        assert image_path.read_bytes().startswith(b"\xff\xd8\xff")
