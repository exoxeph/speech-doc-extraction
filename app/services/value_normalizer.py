import re

from app.services.models import LabValue


_PLAIN_NUMBER = re.compile(r"^[+-]?\d+(?:,\d{3})*(?:\.\d+)?$|^[+-]?\d+(?:\.\d+)?$")
_QUALIFIED_NUMBER = re.compile(
    r"^(?P<operator><=|>=|<|>)\s*(?P<number>[+-]?\d+(?:,\d{3})*(?:\.\d+)?|[+-]?\d+(?:\.\d+)?)$"
)
_SCIENTIFIC_NUMBER = re.compile(
    r"^(?P<base>[+-]?\d+(?:\.\d+)?)\s*(?:x|\*)\s*10\^?(?P<exponent>[+-]?\d+)$",
    flags=re.IGNORECASE,
)
_RANGE = re.compile(r"^[+-]?\d+(?:\.\d+)?\s*-\s*[+-]?\d+(?:\.\d+)?$")


def normalize_lab_value(text: str) -> LabValue | None:
    candidate = text.strip()
    if not candidate:
        return None

    if _RANGE.match(candidate):
        return None

    qualified = _QUALIFIED_NUMBER.match(candidate)
    if qualified:
        numeric = _parse_number(qualified.group("number"))
        return LabValue(
            numeric=numeric,
            operator=qualified.group("operator"),
            raw=candidate,
        )

    scientific = _SCIENTIFIC_NUMBER.match(candidate)
    if scientific:
        numeric = float(scientific.group("base")) * (10 ** int(scientific.group("exponent")))
        return LabValue(numeric=numeric, raw=candidate)

    if _PLAIN_NUMBER.match(candidate):
        return LabValue(numeric=_parse_number(candidate), raw=candidate)

    return None


def _parse_number(text: str) -> float:
    return float(text.replace(",", ""))
