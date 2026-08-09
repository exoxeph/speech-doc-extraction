import pytest

from app.services.value_normalizer import normalize_lab_value


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12.5", 12.5),
        ("12,500", 12500.0),
        ("1.2 x 10^3", 1200.0),
    ],
)
def test_normalize_supported_numeric_values(raw: str, expected: float) -> None:
    value = normalize_lab_value(raw)

    assert value is not None
    assert value.kind == "scalar"
    assert value.numeric == expected
    assert value.operator is None
    assert value.range is None
    assert value.raw == raw


def test_normalize_qualified_numeric_value() -> None:
    value = normalize_lab_value("<0.5")

    assert value is not None
    assert value.kind == "scalar"
    assert value.numeric == 0.5
    assert value.operator == "<"
    assert value.range is None
    assert value.raw == "<0.5"


def test_normalize_range_value_keeps_raw_without_single_numeric_value() -> None:
    value = normalize_lab_value("0.8 - 1.2")

    assert value is not None
    assert value.kind == "range"
    assert value.numeric is None
    assert value.operator is None
    assert value.range is not None
    assert value.range.lower == 0.8
    assert value.range.upper == 1.2
    assert value.raw == "0.8 - 1.2"


def test_normalize_refuses_malformed_or_ambiguous_value() -> None:
    assert normalize_lab_value("1.2 x 1043") is None
