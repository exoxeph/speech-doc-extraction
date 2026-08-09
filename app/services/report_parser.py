import re

from app.services.models import LabResult
from app.services.unit_normalizer import normalize_unit
from app.services.value_normalizer import normalize_lab_value


def parse_lab_result_row(line: str) -> LabResult | None:
    if "|" in line:
        return _parse_pipe_result_row(line)

    parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
    if len(parts) < 3:
        return _parse_collapsed_result_row(line)

    test_name = parts[0]
    value = normalize_lab_value(parts[1])
    if value is None:
        return None

    unit = normalize_unit(parts[2])
    reference_range = _normalize_reference_range(parts[3]) if len(parts) >= 4 else ""
    flag = parts[4] if len(parts) >= 5 else ""

    return LabResult(
        test_name=test_name,
        value=value,
        unit=unit,
        reference_range=reference_range,
        flag=flag,
        raw_line=line,
    )


def _parse_pipe_result_row(line: str) -> LabResult | None:
    parts = [part.strip() for part in line.split("|")]
    if len(parts) < 3:
        return None

    test_name = parts[0]
    if test_name.lower() in {"test name", "---"}:
        return None

    value = normalize_lab_value(parts[1])
    if value is None:
        return None

    reference_range = _normalize_reference_range(parts[3]) if len(parts) >= 4 else ""
    flag = parts[4] if len(parts) >= 5 else ""

    return LabResult(
        test_name=test_name,
        value=value,
        unit=normalize_unit(parts[2]),
        reference_range=reference_range,
        flag=flag,
        raw_line=line,
    )


def _parse_collapsed_result_row(line: str) -> LabResult | None:
    match = re.match(
        r"^(?P<test_name>.+?)\s+"
        r"(?P<value>(?:<=|>=|<|>)?\s*[+-]?\d+(?:,\d{3})*(?:\.\d+)?)\s+"
        r"(?P<unit>\S+)\s+"
        r"(?P<reference_range>[+-]?\d+(?:,\d{3})*(?:\.\d+)?\s*-\s*[+-]?\d+(?:,\d{3})*(?:\.\d+)?)"
        r"(?:\s+(?P<flag>[A-Za-z]+))?$",
        line,
    )
    if not match:
        return None

    value = normalize_lab_value(match.group("value").replace(" ", ""))
    if value is None:
        return None

    return LabResult(
        test_name=match.group("test_name").strip(),
        value=value,
        unit=normalize_unit(match.group("unit")),
        reference_range=_normalize_reference_range(match.group("reference_range")),
        flag=match.group("flag") or "",
        raw_line=line,
    )


def parse_lab_result_rows(lines: list[str]) -> list[LabResult]:
    results: list[LabResult] = []
    for line in lines:
        result = parse_lab_result_row(line)
        if result is not None:
            results.append(result)

    return results


def _normalize_reference_range(reference_range: str) -> str:
    stripped = reference_range.strip()
    compact = re.sub(r"[^a-z/]", "", stripped.lower())
    if compact in {"na", "n/a", "/a", "fa", "ta", "wa"} or compact.endswith("/a"):
        return "N/A"

    return stripped
