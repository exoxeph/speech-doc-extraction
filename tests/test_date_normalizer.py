import pytest

from app.services.date_normalizer import normalize_report_date


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("2026-08-08", "2026-08-08"),
        ("8 Aug 2026", "2026-08-08"),
        ("August 8, 2026", "2026-08-08"),
        ("13/04/2026", "2026-04-13"),
        ("04/13/2026", "2026-04-13"),
    ],
)
def test_normalize_unambiguous_report_dates(raw: str, expected: str) -> None:
    assert normalize_report_date(raw) == expected


@pytest.mark.parametrize("raw", ["03/04/2026", "2026-02-30", "not a date", ""])
def test_normalize_report_date_refuses_invalid_or_ambiguous_dates(raw: str) -> None:
    assert normalize_report_date(raw) is None
