import re

from app.services.models import LabResult
from app.services.unit_normalizer import normalize_unit
from app.services.value_normalizer import normalize_lab_value


def parse_lab_result_row(line: str) -> LabResult | None:
    parts = [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]
    if len(parts) < 3:
        return None

    test_name = parts[0]
    value = normalize_lab_value(parts[1])
    if value is None:
        return None

    unit = normalize_unit(parts[2])
    reference_range = parts[3] if len(parts) >= 4 else ""
    flag = parts[4] if len(parts) >= 5 else ""

    return LabResult(
        test_name=test_name,
        value=value,
        unit=unit,
        reference_range=reference_range,
        flag=flag,
        raw_line=line,
    )


def parse_lab_result_rows(lines: list[str]) -> list[LabResult]:
    results: list[LabResult] = []
    for line in lines:
        result = parse_lab_result_row(line)
        if result is not None:
            results.append(result)

    return results
