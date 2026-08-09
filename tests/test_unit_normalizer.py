import pytest

from app.services.unit_normalizer import normalize_unit


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("gm/dl", "g/dL"),
        ("g/dl", "g/dL"),
        ("g/dL", "g/dL"),
        ("mg/dL", "mg/dL"),
        ("mg/dl", "mg/dL"),
        ("mmol/L", "mmol/L"),
        ("10^3/µL", "10^3/uL"),
    ],
)
def test_normalize_known_laboratory_units(raw: str, expected: str) -> None:
    assert normalize_unit(raw) == expected


def test_normalize_unknown_unit_preserves_original_text() -> None:
    assert normalize_unit("cells per mystery") == "cells per mystery"


def test_normalize_unit_strips_surrounding_whitespace_only() -> None:
    assert normalize_unit("  gm/dl  ") == "g/dL"
