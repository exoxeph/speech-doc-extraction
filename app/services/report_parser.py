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
    pending_test_line: str | None = None
    for line in lines:
        result = parse_lab_result_row(line)
        if result is not None:
            results.append(result)
            pending_test_line = None
            continue

        if pending_test_line is not None:
            multiline_result = _parse_observed_value_row(pending_test_line, line)
            if multiline_result is not None:
                results.append(multiline_result)
                pending_test_line = None
                continue

        if _looks_like_test_name_line(line):
            pending_test_line = line

    return results


def _parse_observed_value_row(test_line: str, value_line: str) -> LabResult | None:
    normalized_line = value_line.replace("—", " ")
    normalized_line = re.sub(
        r"\s+[A-Za-z]-\s+(reference\s+range\b)",
        r" \1",
        normalized_line,
        flags=re.IGNORECASE,
    )
    match = re.search(
        r"\bobserved\s+value\b\s*[:.]?\s*"
        r"(?P<value>(?:<=|>=|<|>)?\s*[^\s]+(?:\s*(?:x|\*)\s*10\^?\d+)?)\s+"
        r"(?P<unit>.+?)"
        r"(?:\s+reference\s+range\s*[:!]?\s*(?P<reference_range>.*))?$",
        normalized_line,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    value = normalize_lab_value(match.group("value"))
    if value is None:
        return None

    return LabResult(
        test_name=_clean_test_name(test_line),
        value=value,
        unit=normalize_unit(match.group("unit")),
        reference_range=_normalize_reference_range(match.group("reference_range") or ""),
        flag="",
        raw_line=f"{test_line}\n{value_line}",
    )


def _looks_like_test_name_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or "observed value" in stripped.lower():
        return False

    return bool(
        "[" in stripped
        or re.search(
            r"\b(glucose|urea|creatinine|calcium|sodium|potassium|chloride|hemoglobin|platelet|crp)\b",
            stripped,
            re.IGNORECASE,
        )
    )


def _clean_test_name(line: str) -> str:
    stripped = line.strip()
    without_number = re.sub(r"^\d+[\).,]\s*", "", stripped).strip()
    without_marker = without_number.lstrip(" ,.;:%)]").strip()
    return re.sub(
        r"\s*[:;]\s*(?:n/?a|w/?a)$",
        "",
        without_marker,
        flags=re.IGNORECASE,
    ).strip()


def _normalize_reference_range(reference_range: str) -> str:
    stripped = reference_range.strip()
    compact = re.sub(r"[^a-z/]", "", stripped.lower())
    if compact in {"na", "n/a", "/a", "fa", "ta", "wa"} or compact.endswith("/a"):
        return "N/A"

    return stripped
