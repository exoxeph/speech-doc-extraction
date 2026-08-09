import pytest

from app.services.value_normalizer import normalize_lab_value


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12.5", 12.5),
        ("12,500", 12500.0),
        ("1.2 x 10^3", 1200.0),
        ("1.2 * 10^3", 1200.0),
        ("2,0", 2.0),
        ("4.@", 4.0),
    ],
)
def test_normalize_supported_numeric_values(raw: str, expected: float) -> None:
    value = normalize_lab_value(raw)

    assert value is not None
    assert value.numeric == expected
    assert value.raw == raw


def test_normalize_qualified_numeric_value() -> None:
    value = normalize_lab_value("<0.5")

    assert value is not None
    assert value.numeric == 0.5
    assert value.operator == "<"
    assert value.raw == "<0.5"


@pytest.mark.parametrize("raw", ["", "Hemoqlobin ??13.? mg??", "0.8 - 1.2"])
def test_normalize_refuses_malformed_or_ambiguous_values(raw: str) -> None:
    assert normalize_lab_value(raw) is None
